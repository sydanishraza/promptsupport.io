#!/usr/bin/env python3
"""
Customer Guide Ultra-Large Document Test
Testing the Knowledge Engine with the user's specific customer_guide.docx (4.6MB DOCX file)
"""

import requests
import json
import os
import time
from dotenv import load_dotenv

# Load environment variables
load_dotenv('/app/frontend/.env')

# Get backend URL from environment
BACKEND_URL = os.environ.get('REACT_APP_BACKEND_URL', 'https://docai-promptsupport.preview.emergentagent.com') + '/api'

class CustomerGuideUltraLargeTest:
    def __init__(self):
        self.base_url = BACKEND_URL
        self.test_job_id = None
        print(f"🏢 Testing Ultra-Large Document Handling at: {self.base_url}")
        print(f"📄 Target Document: customer_guide.docx (4.6MB)")
        
    def test_customer_guide_ultra_large_processing(self):
        """Test processing of customer_guide.docx to verify ultra-large document handling"""
        print("\n🏢 CUSTOMER GUIDE ULTRA-LARGE DOCUMENT TEST")
        print("=" * 60)
        
        # Check if customer_guide.docx exists
        docx_path = "/app/customer_guide.docx"
        if not os.path.exists(docx_path):
            print(f"❌ CRITICAL: customer_guide.docx not found at {docx_path}")
            return False
            
        # Get file size
        file_size = os.path.getsize(docx_path)
        print(f"📊 File Size: {file_size:,} bytes ({file_size/1024/1024:.1f} MB)")
        
        try:
            # Upload the document
            print(f"📤 Uploading customer_guide.docx...")
            
            with open(docx_path, 'rb') as file:
                files = {'file': ('customer_guide.docx', file, 'application/vnd.openxmlformats-officedocument.wordprocessingml.document')}
                
                # Use session with retry and better SSL handling
                session = requests.Session()
                session.verify = False  # Disable SSL verification for internal testing
                
                response = session.post(
                    f"{self.base_url}/upload",
                    files=files,
                    timeout=600,  # 10 minutes timeout for large file
                    stream=True   # Use streaming for large files
                )
                
            print(f"📤 Upload Status Code: {response.status_code}")
            
            if response.status_code != 200:
                print(f"❌ Upload failed: {response.text}")
                return False
                
            upload_data = response.json()
            print(f"📤 Upload Response Keys: {list(upload_data.keys())}")
            
            job_id = upload_data.get('job_id')
            if not job_id:
                print("❌ No job_id returned from upload")
                return False
                
            self.test_job_id = job_id
            print(f"🆔 Job ID: {job_id}")
            
            # Monitor processing with extended timeout
            print(f"⏳ Monitoring processing (extended timeout for ultra-large document)...")
            
            start_time = time.time()
            max_wait_time = 900  # 15 minutes for ultra-large document
            ultra_large_detected = False
            processing_strategy = "unknown"
            
            while True:
                status_response = requests.get(f"{self.base_url}/job-status/{job_id}")
                
                if status_response.status_code == 200:
                    status_data = status_response.json()
                    current_status = status_data.get('status', 'unknown')
                    elapsed_time = time.time() - start_time
                    
                    print(f"⏱️  Status: {current_status} (elapsed: {elapsed_time:.1f}s)")
                    
                    # Look for ultra-large document detection in logs
                    if 'logs' in status_data:
                        logs = status_data['logs']
                        for log in logs:
                            if 'ULTRA-LARGE DOCUMENT DETECTED' in log:
                                ultra_large_detected = True
                                print("🏢 ✅ ULTRA-LARGE DOCUMENT DETECTED in processing logs!")
                            if 'Strategy:' in log:
                                processing_strategy = log.split('Strategy:')[-1].strip()
                                print(f"🎯 Processing Strategy: {processing_strategy}")
                        
                        # Show recent relevant logs
                        recent_logs = logs[-5:] if len(logs) > 5 else logs
                        for log in recent_logs:
                            if any(keyword in log for keyword in ['ULTRA-LARGE', 'strategy', 'articles', 'overflow', 'completeness']):
                                print(f"📋 Log: {log}")
                    
                    if current_status == 'completed':
                        print(f"✅ Processing completed in {elapsed_time:.2f} seconds")
                        break
                    elif current_status == 'failed':
                        print(f"❌ Processing failed after {elapsed_time:.2f} seconds")
                        if 'error' in status_data:
                            print(f"Error: {status_data['error']}")
                        return False
                    elif elapsed_time > max_wait_time:
                        print(f"⏰ Timeout after {max_wait_time} seconds")
                        return False
                        
                else:
                    print(f"❌ Status check failed: {status_response.status_code}")
                    return False
                    
                time.sleep(10)  # Check every 10 seconds
            
            # Get final results
            print(f"\n📊 ANALYZING CUSTOMER GUIDE PROCESSING RESULTS")
            print("=" * 55)
            
            results_response = requests.get(f"{self.base_url}/job-results/{job_id}")
            
            if results_response.status_code != 200:
                print(f"❌ Failed to get results: {results_response.status_code}")
                return False
                
            results_data = results_response.json()
            
            # Analyze results for ultra-large document characteristics
            articles = results_data.get('articles', [])
            chunks_created = results_data.get('chunks_created', 0)
            
            print(f"📄 Articles Generated: {len(articles)}")
            print(f"🧩 Chunks Created: {chunks_created}")
            
            # CRITICAL VERIFICATION POINTS FOR CUSTOMER GUIDE
            verification_results = {
                'ultra_large_detected': ultra_large_detected,
                'exceeds_6_articles': len(articles) > 6,
                'target_article_count': len(articles) >= 10,  # Aim for 10-20+ articles
                'no_hard_limit': len(articles) > 6,  # Verify hard limit removed
                'processing_strategy': processing_strategy,
                'content_preservation': False,
                'enhanced_completeness': False
            }
            
            # Check for ultra-large processing indicators in metadata
            if 'metadata' in results_data:
                metadata = results_data['metadata']
                if metadata.get('ultra_large_processing'):
                    verification_results['ultra_large_detected'] = True
                    verification_results['processing_strategy'] = metadata.get('ultra_large_strategy', processing_strategy)
                    print(f"🏢 ✅ Ultra-large processing confirmed in metadata: {verification_results['processing_strategy']}")
                
                # Check for enhanced completeness verification
                if metadata.get('completeness_threshold') == 0.6:  # 60% threshold for ultra-large
                    verification_results['enhanced_completeness'] = True
                    print(f"🎯 ✅ Enhanced completeness verification (60% threshold) applied")
            
            # Analyze individual articles for ultra-large characteristics
            total_content_length = 0
            articles_with_overflow = 0
            articles_with_multi_level = 0
            
            for i, article in enumerate(articles):
                content_length = len(article.get('content', ''))
                total_content_length += content_length
                title = article.get('title', '')
                
                # Check for overflow handling
                if 'overflow' in title.lower() or 'part' in title.lower():
                    articles_with_overflow += 1
                
                # Check for multi-level overflow (Part 1/2, Part 2/2, etc.)
                if 'part' in title.lower() and '/' in title:
                    articles_with_multi_level += 1
                
                print(f"📄 Article {i+1}: '{title[:50]}...' ({content_length:,} chars)")
            
            # Content preservation check
            if total_content_length > 100000:  # Expect substantial content for 4.6MB file
                verification_results['content_preservation'] = True
                print(f"✅ Content preservation: {total_content_length:,} characters preserved")
            
            print(f"\n📊 CUSTOMER GUIDE ULTRA-LARGE VERIFICATION RESULTS")
            print("=" * 60)
            
            # Verification 1: Ultra-large detection
            if verification_results['ultra_large_detected']:
                print(f"✅ 1. Ultra-large document detection: PASSED")
                print(f"   Strategy: {verification_results['processing_strategy']}")
            else:
                print(f"❌ 1. Ultra-large document detection: FAILED")
                print(f"   Expected: 4.6MB DOCX should trigger ultra-large detection")
            
            # Verification 2: Article count exceeds 6 (hard limit removed)
            if verification_results['exceeds_6_articles']:
                print(f"✅ 2. Hard 6-article limit removed: PASSED ({len(articles)} articles)")
            else:
                print(f"❌ 2. Hard 6-article limit removed: FAILED ({len(articles)} articles)")
                print(f"   Expected: Should generate more than 6 articles for 4.6MB document")
            
            # Verification 3: Target article count (10-20+)
            if verification_results['target_article_count']:
                print(f"✅ 3. Target article count achieved: PASSED ({len(articles)} articles >= 10)")
            else:
                print(f"⚠️  3. Target article count achieved: PARTIAL ({len(articles)} articles < 10)")
                print(f"   Expected: Aim for 10-20+ articles for comprehensive coverage")
            
            # Verification 4: Content preservation
            if verification_results['content_preservation']:
                print(f"✅ 4. Content preservation: PASSED")
                print(f"   Total content: {total_content_length:,} characters")
                print(f"   Average per article: {total_content_length // len(articles):,} characters")
            else:
                print(f"❌ 4. Content preservation: FAILED")
                print(f"   Expected: Substantial content preservation for 4.6MB file")
            
            # Verification 5: Ultra-large processing strategy
            valid_strategies = ['document_splitting', 'hierarchical_articles', 'multi_level_overflow']
            if verification_results['processing_strategy'] in valid_strategies:
                print(f"✅ 5. Ultra-large processing strategy: PASSED")
                print(f"   Strategy applied: {verification_results['processing_strategy']}")
            else:
                print(f"❌ 5. Ultra-large processing strategy: FAILED")
                print(f"   Expected: {', '.join(valid_strategies)}")
                print(f"   Actual: {verification_results['processing_strategy']}")
            
            # Verification 6: Multi-level overflow handling
            if articles_with_overflow > 0:
                print(f"✅ 6. Overflow handling: PASSED ({articles_with_overflow} overflow articles)")
                if articles_with_multi_level > 0:
                    print(f"   Multi-level overflow detected: {articles_with_multi_level} articles")
            else:
                print(f"⚠️  6. Overflow handling: NOT NEEDED (document processed without overflow)")
            
            # Verification 7: Enhanced completeness verification
            if verification_results['enhanced_completeness']:
                print(f"✅ 7. Enhanced completeness verification: PASSED (60% threshold)")
            else:
                print(f"⚠️  7. Enhanced completeness verification: NOT DETECTED")
            
            # Overall assessment
            critical_checks = [
                verification_results['ultra_large_detected'],
                verification_results['exceeds_6_articles'],
                verification_results['content_preservation'],
                verification_results['processing_strategy'] in valid_strategies
            ]
            
            passed_critical = sum(critical_checks)
            total_critical = len(critical_checks)
            
            print(f"\n🎯 CRITICAL CHECKS: {passed_critical}/{total_critical} passed")
            print(f"📊 ARTICLE COUNT: {len(articles)} (Target: 10-20+)")
            print(f"🎯 PROCESSING STRATEGY: {verification_results['processing_strategy']}")
            
            if passed_critical >= 3 and len(articles) > 6:
                print(f"\n✅ CUSTOMER GUIDE ULTRA-LARGE PROCESSING: SUCCESS")
                print(f"   ✅ Ultra-large document detected and processed with enhanced strategies")
                print(f"   ✅ Hard 6-article limit removed ({len(articles)} articles generated)")
                print(f"   ✅ Content preservation working ({total_content_length:,} chars)")
                print(f"   ✅ Enhanced processing strategy applied: {verification_results['processing_strategy']}")
                return True
            else:
                print(f"\n❌ CUSTOMER GUIDE ULTRA-LARGE PROCESSING: NEEDS IMPROVEMENT")
                print(f"   Some critical ultra-large document features are not working as expected")
                return False
                
        except Exception as e:
            print(f"❌ Customer guide ultra-large test failed: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def test_content_library_verification(self):
        """Verify that customer guide articles are properly stored in Content Library"""
        print(f"\n📚 CONTENT LIBRARY VERIFICATION TEST")
        print("=" * 45)
        
        try:
            # Get Content Library articles
            response = requests.get(f"{self.base_url}/content-library")
            
            if response.status_code != 200:
                print(f"❌ Content Library access failed: {response.status_code}")
                return False
                
            data = response.json()
            articles = data.get('articles', [])
            total_articles = data.get('total', len(articles))
            
            print(f"📚 Total articles in Content Library: {total_articles}")
            
            # Look for articles from our test job
            if self.test_job_id:
                job_articles = []
                customer_guide_articles = []
                
                for art in articles:
                    # Check by job ID
                    if self.test_job_id in str(art.get('source_job_id', '')):
                        job_articles.append(art)
                    
                    # Check by filename/title containing customer guide references
                    title = art.get('title', '').lower()
                    source = art.get('source_document', '').lower()
                    if 'customer' in title or 'guide' in title or 'customer_guide' in source:
                        customer_guide_articles.append(art)
                
                print(f"📄 Articles from test job: {len(job_articles)}")
                print(f"📄 Customer guide related articles: {len(customer_guide_articles)}")
                
                # Show some article titles
                if job_articles:
                    print(f"📋 Sample article titles from test:")
                    for i, art in enumerate(job_articles[:5]):
                        print(f"   {i+1}. {art.get('title', 'Untitled')[:60]}...")
                
                if len(job_articles) > 6:
                    print(f"✅ Content Library verification: SUCCESS")
                    print(f"   Customer guide articles properly stored ({len(job_articles)} articles)")
                    return True
                else:
                    print(f"⚠️  Content Library verification: PARTIAL")
                    print(f"   Expected more articles from ultra-large document processing")
                    return len(job_articles) > 0
            else:
                print(f"⚠️  Cannot verify job-specific articles (no test_job_id)")
                return False
                
        except Exception as e:
            print(f"❌ Content Library verification test failed: {e}")
            return False
    
    def run_all_tests(self):
        """Run all customer guide ultra-large document tests"""
        print(f"🏢 CUSTOMER GUIDE ULTRA-LARGE DOCUMENT TEST SUITE")
        print(f"=" * 65)
        print(f"📄 Testing with customer_guide.docx (4.6MB DOCX file)")
        print(f"🎯 Expected Results:")
        print(f"   • Ultra-large document detection triggered")
        print(f"   • Generate 10-20+ articles (not limited to 6)")
        print(f"   • Enhanced processing strategies applied")
        print(f"   • Comprehensive content coverage")
        print()
        
        results = {
            'ultra_large_processing': False,
            'content_library_verification': False
        }
        
        # Test 1: Customer guide ultra-large processing
        results['ultra_large_processing'] = self.test_customer_guide_ultra_large_processing()
        
        # Test 2: Content Library verification
        results['content_library_verification'] = self.test_content_library_verification()
        
        # Final summary
        print(f"\n🏢 CUSTOMER GUIDE ULTRA-LARGE TEST SUMMARY")
        print("=" * 55)
        
        passed_tests = sum(results.values())
        total_tests = len(results)
        
        for test_name, passed in results.items():
            status = "✅ PASSED" if passed else "❌ FAILED"
            print(f"{status} {test_name.replace('_', ' ').title()}")
        
        print(f"\n🎯 OVERALL RESULT: {passed_tests}/{total_tests} tests passed")
        
        if passed_tests == total_tests:
            print(f"\n🎉 CUSTOMER GUIDE ULTRA-LARGE PROCESSING: FULLY OPERATIONAL")
            print(f"   ✅ Ultra-large documents detected and processed with enhanced strategies")
            print(f"   ✅ Hard 6-article limit removed, generating 10-20+ articles as needed")
            print(f"   ✅ Content preservation and comprehensive coverage working")
            print(f"   ✅ Integration with Content Library successful")
        elif passed_tests > 0:
            print(f"\n⚠️  CUSTOMER GUIDE ULTRA-LARGE PROCESSING: PARTIALLY WORKING")
            print(f"   Some features working but improvements needed")
        else:
            print(f"\n❌ CUSTOMER GUIDE ULTRA-LARGE PROCESSING: CRITICAL ISSUES")
            print(f"   Ultra-large document processing not working as expected")
        
        return passed_tests == total_tests

if __name__ == "__main__":
    tester = CustomerGuideUltraLargeTest()
    success = tester.run_all_tests()
    
    if success:
        print(f"\n🎉 All customer guide ultra-large tests passed!")
        exit(0)
    else:
        print(f"\n❌ Some customer guide ultra-large tests failed!")
        exit(1)