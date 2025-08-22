#!/usr/bin/env python3
"""
Focused Critical Issues Testing
Quick tests for the three critical issues with shorter timeouts
"""

import requests
import json
import os
import re
import pymongo
from dotenv import load_dotenv

# Load environment variables
load_dotenv('/app/frontend/.env')

# Get backend URL from environment
BACKEND_URL = os.environ.get('REACT_APP_BACKEND_URL', 'https://smartdoc-v2.preview.emergentagent.com') + '/api'
MONGO_URL = "mongodb://localhost:27017/"

class FocusedCriticalTest:
    def __init__(self):
        self.base_url = BACKEND_URL
        try:
            self.mongo_client = pymongo.MongoClient(MONGO_URL, serverSelectionTimeoutMS=5000)
            self.db = self.mongo_client.promptsupport_db
            # Test connection
            self.mongo_client.server_info()
            print(f"✅ MongoDB connected: {MONGO_URL}")
        except Exception as e:
            print(f"❌ MongoDB connection failed: {e}")
            self.db = None
        
        print(f"Testing at: {self.base_url}")
    
    def test_backend_health(self):
        """Test basic backend connectivity"""
        print("\n🔍 Testing Backend Health...")
        try:
            response = requests.get(f"{self.base_url}/health", timeout=10)
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Backend healthy: {data.get('status')}")
                return True
            else:
                print(f"❌ Backend unhealthy: {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ Backend connection failed: {e}")
            return False
    
    def test_asset_library_api(self):
        """Test Asset Library API directly"""
        print("\n🔍 Testing Asset Library API...")
        try:
            response = requests.get(f"{self.base_url}/assets", timeout=15)
            if response.status_code == 200:
                data = response.json()
                total_assets = data.get('total', 0)
                assets = data.get('assets', [])
                print(f"✅ Asset Library API working: {total_assets} total assets")
                print(f"✅ Assets returned: {len(assets)}")
                
                # Check for PDF images
                pdf_images = [a for a in assets if 'pdf' in a.get('filename', '').lower() or 'png' in a.get('filename', '').lower()]
                print(f"📊 PDF/Image assets: {len(pdf_images)}")
                
                if pdf_images:
                    print("✅ ISSUE 1 STATUS: PDF images found in Asset Library")
                    for asset in pdf_images[:3]:
                        print(f"  - {asset.get('filename')} ({asset.get('file_size', 0)} bytes)")
                    return True
                else:
                    print("⚠️ ISSUE 1 STATUS: No PDF images found in Asset Library")
                    return False
            else:
                print(f"❌ Asset Library API failed: {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ Asset Library API error: {e}")
            return False
    
    def test_content_library_for_empty_articles(self):
        """Test Content Library for empty articles"""
        print("\n🔍 Testing Content Library for Empty Articles...")
        try:
            response = requests.get(f"{self.base_url}/content-library", timeout=15)
            if response.status_code == 200:
                data = response.json()
                articles = data.get('articles', [])
                total_articles = data.get('total', len(articles))
                
                print(f"✅ Content Library API working: {total_articles} total articles")
                print(f"✅ Articles returned: {len(articles)}")
                
                # Check for empty articles
                empty_articles = []
                short_articles = []
                
                for article in articles:
                    content = article.get('content', '')
                    # Remove HTML tags for accurate count
                    clean_content = re.sub(r'<[^>]+>', '', content).strip()
                    content_length = len(clean_content)
                    
                    if content_length < 100:
                        empty_articles.append({
                            'title': article.get('title', 'Untitled'),
                            'length': content_length
                        })
                    elif content_length < 300:
                        short_articles.append({
                            'title': article.get('title', 'Untitled'),
                            'length': content_length
                        })
                
                print(f"📊 Empty articles (< 100 chars): {len(empty_articles)}")
                print(f"📊 Short articles (< 300 chars): {len(short_articles)}")
                
                if empty_articles:
                    print("❌ ISSUE 3 STATUS: Empty articles found")
                    for article in empty_articles[:5]:
                        print(f"  - '{article['title']}' ({article['length']} chars)")
                    return False
                else:
                    print("✅ ISSUE 3 STATUS: No empty articles found")
                    return True
                    
            else:
                print(f"❌ Content Library API failed: {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ Content Library API error: {e}")
            return False
    
    def test_pdf_content_coverage(self):
        """Test PDF content coverage by analyzing existing articles"""
        print("\n🔍 Testing PDF Content Coverage...")
        try:
            response = requests.get(f"{self.base_url}/content-library", timeout=15)
            if response.status_code == 200:
                data = response.json()
                articles = data.get('articles', [])
                
                # Look for PDF-generated articles
                pdf_articles = []
                for article in articles:
                    title = article.get('title', '').lower()
                    source = article.get('source_document', '').lower()
                    
                    if 'pdf' in title or 'pdf' in source or '.pdf' in source:
                        content = article.get('content', '')
                        clean_content = re.sub(r'<[^>]+>', '', content).strip()
                        pdf_articles.append({
                            'title': article.get('title', 'Untitled'),
                            'length': len(clean_content),
                            'has_tables': '<table' in content.lower() or 'table' in clean_content.lower(),
                            'has_headers': any(tag in content.lower() for tag in ['<h1', '<h2', '<h3']),
                            'comprehensive': len(clean_content) > 1000
                        })
                
                print(f"📊 PDF articles found: {len(pdf_articles)}")
                
                if pdf_articles:
                    comprehensive_articles = [a for a in pdf_articles if a['comprehensive']]
                    articles_with_tables = [a for a in pdf_articles if a['has_tables']]
                    articles_with_headers = [a for a in pdf_articles if a['has_headers']]
                    
                    print(f"📊 Comprehensive articles (>1000 chars): {len(comprehensive_articles)}")
                    print(f"📊 Articles with tables: {len(articles_with_tables)}")
                    print(f"📊 Articles with headers: {len(articles_with_headers)}")
                    
                    if len(comprehensive_articles) > 0:
                        print("✅ ISSUE 2 STATUS: PDF content coverage appears comprehensive")
                        return True
                    else:
                        print("❌ ISSUE 2 STATUS: PDF content coverage may be incomplete")
                        return False
                else:
                    print("⚠️ ISSUE 2 STATUS: No PDF articles found to analyze")
                    return False
                    
            else:
                print(f"❌ Content Library API failed: {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ PDF content coverage test error: {e}")
            return False
    
    def test_mongodb_direct_access(self):
        """Test MongoDB direct access for Asset Library"""
        print("\n🔍 Testing MongoDB Direct Access...")
        if self.db is None:
            print("❌ MongoDB not available")
            return False
        
        try:
            # Check assets collection
            assets_count = self.db.assets.count_documents({})
            print(f"✅ MongoDB assets collection: {assets_count} documents")
            
            # Look for PDF images
            pdf_assets = list(self.db.assets.find({
                "$or": [
                    {"filename": {"$regex": "pdf.*\\.png", "$options": "i"}},
                    {"filename": {"$regex": ".*\\.png", "$options": "i"}},
                    {"source": "training_engine_extraction"}
                ]
            }).limit(10))
            
            print(f"📊 PDF/Image assets in MongoDB: {len(pdf_assets)}")
            
            if pdf_assets:
                print("✅ ISSUE 1 MONGODB: PDF images found in database")
                for asset in pdf_assets[:3]:
                    print(f"  - {asset.get('filename')} (ID: {asset.get('id')})")
                return True
            else:
                print("❌ ISSUE 1 MONGODB: No PDF images in database")
                return False
                
        except Exception as e:
            print(f"❌ MongoDB direct access error: {e}")
            return False
    
    def run_focused_tests(self):
        """Run focused tests for all three critical issues"""
        print("🚀 FOCUSED CRITICAL ISSUES TESTING")
        print("="*60)
        
        results = []
        
        # Basic connectivity
        health_ok = self.test_backend_health()
        if not health_ok:
            print("❌ Backend not responding - cannot continue tests")
            return 0, 4
        
        # Test Issue 1: PDF Images in Asset Library
        asset_api_ok = self.test_asset_library_api()
        mongodb_ok = self.test_mongodb_direct_access()
        issue1_resolved = asset_api_ok or mongodb_ok
        results.append(("PDF Images in Asset Library", issue1_resolved))
        
        # Test Issue 2: PDF Content Coverage
        issue2_resolved = self.test_pdf_content_coverage()
        results.append(("PDF Content Coverage", issue2_resolved))
        
        # Test Issue 3: Empty DOCX Articles
        issue3_resolved = self.test_content_library_for_empty_articles()
        results.append(("Empty DOCX Articles", issue3_resolved))
        
        # Summary
        print("\n" + "="*60)
        print("📊 FOCUSED TESTING SUMMARY")
        print("="*60)
        
        passed = 0
        total = len(results)
        
        for issue_name, result in results:
            status = "✅ RESOLVED" if result else "❌ NOT RESOLVED"
            print(f"{status}: {issue_name}")
            if result:
                passed += 1
        
        print(f"\n📈 Results: {passed}/{total} critical issues resolved")
        
        return passed, total

if __name__ == "__main__":
    tester = FocusedCriticalTest()
    passed, total = tester.run_focused_tests()