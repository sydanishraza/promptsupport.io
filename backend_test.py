#!/usr/bin/env python3
"""
TICKET 2 Implementation Testing - Stable Anchors + Mini-TOC Systematic Fix
Testing the complete TICKET 2 solution for Mini-TOC anchoring system
"""

import requests
import json
import time
import sys
import re
from datetime import datetime

# Get backend URL from frontend env
try:
    with open('/app/frontend/.env', 'r') as f:
        for line in f:
            if line.startswith('REACT_APP_BACKEND_URL='):
                BACKEND_URL = line.split('=', 1)[1].strip()
                break
    else:
        BACKEND_URL = "https://content-formatter.preview.emergentagent.com"
except:
    BACKEND_URL = "https://content-formatter.preview.emergentagent.com"

API_BASE = f"{BACKEND_URL}/api"

print(f"🧪 TICKET 2 TESTING: Stable Anchors + Mini-TOC Systematic Fix")
print(f"🌐 Backend URL: {BACKEND_URL}")
print(f"📡 API Base: {API_BASE}")
print("=" * 80)

class TICKET2Tester:
    def __init__(self):
        self.test_results = []
        self.total_tests = 0
        self.passed_tests = 0
        
    def log_test(self, test_name, passed, details=""):
        """Log test result"""
        self.total_tests += 1
        if passed:
            self.passed_tests += 1
            status = "✅ PASS"
        else:
            status = "❌ FAIL"
        
        result = {
            "test": test_name,
            "passed": passed,
            "details": details,
            "timestamp": datetime.now().isoformat()
        }
        self.test_results.append(result)
        print(f"{status} | {test_name}")
        if details:
            print(f"    📝 {details}")
        print()
        
        for i, h1 in enumerate(h1_tags):
            h1_analysis["positions"].append(f"H1 #{i+1}")
            h1_analysis["content"].append(h1.get_text().strip())
            
        return h1_analysis
        
    def test_engine_status(self) -> bool:
        """Test V2 engine status and availability"""
        try:
            response = self.session.get(f"{BACKEND_URL}/engine")
            if response.status_code == 200:
                data = response.json()
                engine_status = data.get('engine', 'unknown')
                features = data.get('features', [])
                
                self.log_result(
                    "V2 Engine Status Check",
                    "PASS" if engine_status == 'v2' else "FAIL",
                    f"Engine: {engine_status}, Features: {len(features)} available"
                )
                return engine_status == 'v2'
            else:
                self.log_result("V2 Engine Status Check", "FAIL", f"HTTP {response.status_code}")
                return False
        except Exception as e:
            self.log_result("V2 Engine Status Check", "FAIL", f"Error: {str(e)}")
            return False
            
    def test_document_upload_and_processing(self, file_path: str) -> Dict[str, Any]:
        """Upload document and track V2 processing pipeline"""
        try:
            if not os.path.exists(file_path):
                self.log_result("Document Upload", "FAIL", f"File not found: {file_path}")
                return None
                
            filename = os.path.basename(file_path)
            self.log_result("Document Upload", "INFO", f"Processing {filename}")
            
            # Upload document
            with open(file_path, 'rb') as f:
                files = {'file': (filename, f, 'application/octet-stream')}
                data = {'metadata': json.dumps({'template_id': 'v2_comprehensive'})}
                
                response = self.session.post(f"{BACKEND_URL}/content/upload", files=files, data=data)
                
            if response.status_code != 200:
                self.log_result("Document Upload", "FAIL", f"Upload failed: HTTP {response.status_code}")
                return None
                
            upload_result = response.json()
            job_id = upload_result.get('job_id')
            
            if not job_id:
                self.log_result("Document Upload", "FAIL", "No job_id returned")
                return None
                
            self.log_result("Document Upload", "PASS", f"Job ID: {job_id}")
            
            # Wait for processing to complete
            max_wait = 120  # 2 minutes
            wait_time = 0
            
            while wait_time < max_wait:
                time.sleep(5)
                wait_time += 5
                
                # Check job status
                status_response = self.session.get(f"{BACKEND_URL}/job-status/{job_id}")
                if status_response.status_code == 200:
                    status_data = status_response.json()
                    job_status = status_data.get('status', 'unknown')
                    
                    if job_status == 'completed':
                        self.log_result("V2 Processing", "PASS", f"Processing completed in {wait_time}s")
                        return {
                            'job_id': job_id,
                            'filename': filename,
                            'processing_time': wait_time,
                            'status_data': status_data
                        }
                    elif job_status == 'failed':
                        self.log_result("V2 Processing", "FAIL", f"Processing failed: {status_data.get('error', 'Unknown error')}")
                        return None
                    else:
                        print(f"Processing status: {job_status} (waiting {wait_time}s)")
                        
            self.log_result("V2 Processing", "FAIL", f"Processing timeout after {max_wait}s")
            return None
            
        except Exception as e:
            self.log_result("Document Upload", "FAIL", f"Error: {str(e)}")
            return None
            
    def test_content_library_h1_analysis(self) -> List[Dict[str, Any]]:
        """Analyze H1 tags in content library articles"""
        try:
            response = self.session.get(f"{BACKEND_URL}/content-library")
            if response.status_code != 200:
                self.log_result("Content Library Access", "FAIL", f"HTTP {response.status_code}")
                return []
                
            articles = response.json()
            h1_analysis_results = []
            
            self.log_result("Content Library Access", "PASS", f"Found {len(articles)} articles")
            
            for article in articles[:10] if len(articles) > 10 else articles:  # Analyze first 10 articles
                article_id = article.get('id')
                title = article.get('title', 'Untitled')
                content = article.get('content', '')
                
                h1_analysis = self.count_h1_tags(content)
                
                analysis_result = {
                    'article_id': article_id,
                    'title': title,
                    'h1_analysis': h1_analysis,
                    'content_length': len(content)
                }
                h1_analysis_results.append(analysis_result)
                
                status = "FAIL" if h1_analysis['in_body'] > 0 else "PASS"
                self.log_result(
                    f"H1 Analysis: {title[:50]}",
                    status,
                    f"H1s in body: {h1_analysis['in_body']}, Total H1s: {h1_analysis['total']}"
                )
                
            return h1_analysis_results
            
        except Exception as e:
            self.log_result("Content Library Analysis", "FAIL", f"Error: {str(e)}")
            return []
            
    def test_v2_validation_system(self) -> bool:
        """Test V2 validation system endpoints"""
        try:
            # Test validation diagnostics
            response = self.session.get(f"{BACKEND_URL}/validation/diagnostics")
            if response.status_code == 200:
                validation_data = response.json()
                recent_validations = validation_data.get('recent_validations', [])
                
                self.log_result(
                    "V2 Validation System",
                    "PASS",
                    f"Validation system active, {len(recent_validations)} recent validations"
                )
                
                # Check for H1 validation failures
                h1_failures = 0
                for validation in recent_validations:
                    validation_results = validation.get('validation_results', {})
                    h1_validation = validation_results.get('validate_no_h1_in_body', {})
                    if not h1_validation.get('passed', True):
                        h1_failures += 1
                        
                self.log_result(
                    "H1 Validation Failures",
                    "INFO",
                    f"Found {h1_failures} H1 validation failures in recent validations"
                )
                
                return True
            else:
                self.log_result("V2 Validation System", "FAIL", f"HTTP {response.status_code}")
                return False
                
        except Exception as e:
            self.log_result("V2 Validation System", "FAIL", f"Error: {str(e)}")
            return False
            
    def test_style_processing_h1_fixes(self) -> bool:
        """Test V2 style processing system for H1 fixes"""
        try:
            # Test style diagnostics
            response = self.session.get(f"{BACKEND_URL}/style/diagnostics")
            if response.status_code == 200:
                style_data = response.json()
                recent_results = style_data.get('recent_results', [])
                
                self.log_result(
                    "V2 Style Processing",
                    "PASS",
                    f"Style system active, {len(recent_results)} recent results"
                )
                
                # Check for polish_article_content application
                polish_applications = 0
                for result in recent_results:
                    style_changes = result.get('style_changes', [])
                    for change in style_changes:
                        if 'h1' in change.lower() or 'heading' in change.lower():
                            polish_applications += 1
                            
                self.log_result(
                    "Polish Article Content Fixes",
                    "INFO",
                    f"Found {polish_applications} heading-related style changes"
                )
                
                return True
            else:
                self.log_result("V2 Style Processing", "FAIL", f"HTTP {response.status_code}")
                return False
                
        except Exception as e:
            self.log_result("V2 Style Processing", "FAIL", f"Error: {str(e)}")
            return False
            
    def test_specific_document_h1_tracking(self, file_path: str) -> Dict[str, Any]:
        """Process specific document and track H1 generation through pipeline"""
        try:
            filename = os.path.basename(file_path)
            self.log_result("H1 Pipeline Tracking", "INFO", f"Starting H1 tracking for {filename}")
            
            # Process document
            processing_result = self.test_document_upload_and_processing(file_path)
            if not processing_result:
                return None
                
            job_id = processing_result['job_id']
            
            # Wait a bit for all processing to complete
            time.sleep(10)
            
            # Get content library articles created from this job
            response = self.session.get(f"{BACKEND_URL}/content-library")
            if response.status_code != 200:
                self.log_result("H1 Pipeline Tracking", "FAIL", "Cannot access content library")
                return None
                
            articles = response.json()
            
            # Find articles from this processing job (recent articles)
            recent_articles = []
            current_time = time.time()
            
            for article in articles:
                # Check if article was created recently (within last 5 minutes)
                created_at = article.get('created_at')
                if created_at:
                    # Simple heuristic: if it's one of the most recent articles
                    recent_articles.append(article)
                    
            # Take the most recent articles (likely from our processing)
            recent_articles = recent_articles[:5]
            
            h1_tracking_results = {
                'filename': filename,
                'job_id': job_id,
                'articles_analyzed': len(recent_articles),
                'h1_issues': [],
                'total_h1s_found': 0,
                'articles_with_h1_issues': 0
            }
            
            for article in recent_articles:
                title = article.get('title', 'Untitled')
                content = article.get('content', '')
                
                h1_analysis = self.count_h1_tags(content)
                
                if h1_analysis['in_body'] > 0:
                    h1_tracking_results['articles_with_h1_issues'] += 1
                    h1_tracking_results['h1_issues'].append({
                        'article_title': title,
                        'h1_count': h1_analysis['in_body'],
                        'h1_content': h1_analysis['content']
                    })
                    
                h1_tracking_results['total_h1s_found'] += h1_analysis['in_body']
                
            # Log results
            if h1_tracking_results['total_h1s_found'] > 0:
                self.log_result(
                    "H1 Pipeline Tracking",
                    "FAIL",
                    f"Found {h1_tracking_results['total_h1s_found']} H1 tags in {h1_tracking_results['articles_with_h1_issues']} articles"
                )
            else:
                self.log_result(
                    "H1 Pipeline Tracking",
                    "PASS",
                    f"No H1 tags found in article content for {filename}"
                )
                
            return h1_tracking_results
            
        except Exception as e:
            self.log_result("H1 Pipeline Tracking", "FAIL", f"Error: {str(e)}")
            return None
            
    def run_comprehensive_h1_investigation(self):
        """Run comprehensive H1 elimination investigation"""
        print("=" * 80)
        print("TICKET 1 H1 ELIMINATION INVESTIGATION - BACKEND TESTING")
        print("=" * 80)
        
        # Test 1: Engine Status
        engine_ok = self.test_engine_status()
        if not engine_ok:
            print("❌ V2 Engine not available - cannot proceed with testing")
            return
            
        # Test 2: V2 Validation System
        self.test_v2_validation_system()
        
        # Test 3: V2 Style Processing System
        self.test_style_processing_h1_fixes()
        
        # Test 4: Current Content Library H1 Analysis
        self.test_content_library_h1_analysis()
        
        # Test 5: Process specific test documents
        test_documents = [
            "/app/Google_Map_JavaScript_API_Tutorial.docx",
            "/app/Promotions_Configuration_and_Management-v5-20220201_173002.docx",
            "/app/Whisk_Studio_Integration_Guide.pdf"
        ]
        
        h1_tracking_results = []
        for doc_path in test_documents:
            if os.path.exists(doc_path):
                result = self.test_specific_document_h1_tracking(doc_path)
                if result:
                    h1_tracking_results.append(result)
            else:
                self.log_result("Document Processing", "SKIP", f"File not found: {doc_path}")
                
        # Summary Report
        print("\n" + "=" * 80)
        print("H1 ELIMINATION INVESTIGATION SUMMARY")
        print("=" * 80)
        
        total_tests = len(self.test_results)
        passed_tests = len([r for r in self.test_results if r['status'] == 'PASS'])
        failed_tests = len([r for r in self.test_results if r['status'] == 'FAIL'])
        
        print(f"Total Tests: {total_tests}")
        print(f"Passed: {passed_tests}")
        print(f"Failed: {failed_tests}")
        print(f"Success Rate: {(passed_tests/total_tests)*100:.1f}%")
        
        # H1 Issues Summary
        total_h1_issues = sum(r.get('total_h1s_found', 0) for r in h1_tracking_results)
        articles_with_issues = sum(r.get('articles_with_h1_issues', 0) for r in h1_tracking_results)
        
        print(f"\nH1 ELIMINATION ANALYSIS:")
        print(f"Documents Processed: {len(h1_tracking_results)}")
        print(f"Total H1 Tags Found in Article Content: {total_h1_issues}")
        print(f"Articles with H1 Issues: {articles_with_issues}")
        
        if total_h1_issues > 0:
            print(f"\n❌ TICKET 1 H1 ELIMINATION: FAILED")
            print(f"H1 tags are still being injected into article content despite fixes")
            
            # Detailed H1 issue breakdown
            for result in h1_tracking_results:
                if result.get('h1_issues'):
                    print(f"\nDocument: {result['filename']}")
                    for issue in result['h1_issues']:
                        print(f"  - Article: {issue['article_title']}")
                        print(f"    H1 Count: {issue['h1_count']}")
                        print(f"    H1 Content: {issue['h1_content']}")
        else:
            print(f"\n✅ TICKET 1 H1 ELIMINATION: PASSED")
            print(f"No H1 tags found in article content")
            
        return self.test_results

def main():
    """Main test execution"""
    tester = H1TrackingTest()
    results = tester.run_comprehensive_h1_investigation()
    
    # Save results to file
    with open('/app/h1_investigation_results.json', 'w') as f:
        json.dump(results, f, indent=2, default=str)
        
    print(f"\nDetailed results saved to: /app/h1_investigation_results.json")

if __name__ == "__main__":
    main()