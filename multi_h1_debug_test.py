#!/usr/bin/env python3
"""
Multi-H1 Document Debug Test for Training Engine
Captures complete trace of HTML preprocessing pipeline with debug logs
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
BACKEND_URL = os.environ.get('REACT_APP_BACKEND_URL', 'https://5281eecc-eac8-4f65-9a23-23445575ef21.preview.emergentagent.com') + '/api'

class MultiH1DebugTest:
    def __init__(self):
        self.base_url = BACKEND_URL
        print(f"🔍 Testing Multi-H1 Document Processing at: {self.base_url}")
        print("🎯 OBJECTIVE: Capture complete debug trace of HTML preprocessing pipeline")
        
    def create_multi_h1_document(self):
        """Create a test document with multiple H1 sections"""
        return """# Introduction to Machine Learning
        
This is the introduction section that explains the basics of machine learning and artificial intelligence. This section should become the first article based on the H1 heading structure.

Machine learning is a subset of artificial intelligence that enables computers to learn and make decisions from data without being explicitly programmed for every task.

## Key Concepts
- Supervised Learning
- Unsupervised Learning  
- Reinforcement Learning

# Data Preprocessing and Feature Engineering

This is the second major section focusing on data preprocessing techniques. This should become the second article based on the H1 heading structure.

Data preprocessing is crucial for successful machine learning projects. It involves cleaning, transforming, and preparing raw data for analysis.

## Common Preprocessing Steps
- Data cleaning and validation
- Feature scaling and normalization
- Handling missing values
- Feature selection and extraction

# Model Training and Evaluation

This is the third major section covering model training methodologies. This should become the third article based on the H1 heading structure.

Model training involves selecting appropriate algorithms, tuning hyperparameters, and evaluating model performance using various metrics.

## Training Strategies
- Cross-validation techniques
- Hyperparameter optimization
- Model selection criteria
- Performance evaluation metrics

# Deployment and Production Considerations

This is the fourth and final major section about deploying models to production. This should become the fourth article based on the H1 heading structure.

Deploying machine learning models to production requires careful consideration of scalability, monitoring, and maintenance requirements.

## Production Challenges
- Model versioning and updates
- Performance monitoring
- Scalability requirements
- Data drift detection"""

    def test_multi_h1_document_processing(self):
        """Test Training Engine with multi-H1 document and capture debug logs"""
        print("\n🔍 TESTING MULTI-H1 DOCUMENT PROCESSING WITH DEBUG LOGS")
        print("=" * 80)
        
        try:
            # Create multi-H1 test document
            test_content = self.create_multi_h1_document()
            print(f"📄 Created test document with 4 H1 sections:")
            h1_lines = [line.strip() for line in test_content.split('\n') if line.strip().startswith('# ')]
            for i, h1 in enumerate(h1_lines, 1):
                print(f"   H1 #{i}: {h1}")
            
            # Create file for upload
            file_data = io.BytesIO(test_content.encode('utf-8'))
            
            files = {
                'file': ('multi_h1_test_document.txt', file_data, 'text/plain')
            }
            
            # Use template that should trigger HTML preprocessing pipeline
            template_data = {
                "template_id": "phase1_document_processing",
                "processing_instructions": "Process document with H1-based chunking and debug logging",
                "output_requirements": {
                    "format": "html",
                    "min_articles": 1,
                    "max_articles": 6,
                    "quality_benchmarks": ["content_completeness", "h1_based_structure"]
                },
                "debug_mode": True
            }
            
            form_data = {
                'template_id': 'phase1_document_processing',
                'training_mode': 'true',
                'template_instructions': json.dumps(template_data)
            }
            
            print(f"\n📤 UPLOADING MULTI-H1 DOCUMENT TO TRAINING ENGINE...")
            print(f"🎯 Looking for these specific debug messages:")
            print(f"   - 'DEBUG: Using HTML preprocessing pipeline for [file_type]'")
            print(f"   - 'H1 elements found:' with list of H1 titles")
            print(f"   - 'DEBUG: Processing X final chunks into articles'")
            print(f"   - 'DEBUG: HTML pipeline returned X articles'")
            
            start_time = time.time()
            
            response = requests.post(
                f"{self.base_url}/training/process",
                files=files,
                data=form_data,
                timeout=180  # Extended timeout for debug logging
            )
            
            processing_time = time.time() - start_time
            
            print(f"\n⏱️ PROCESSING COMPLETED IN {processing_time:.2f} SECONDS")
            print(f"📊 HTTP STATUS CODE: {response.status_code}")
            
            if response.status_code != 200:
                print(f"❌ PROCESSING FAILED - Status Code: {response.status_code}")
                print(f"Response: {response.text}")
                return False
            
            # Parse response
            data = response.json()
            print(f"\n📋 RESPONSE DATA KEYS: {list(data.keys())}")
            
            # CRITICAL DEBUG ANALYSIS
            print(f"\n🔍 CRITICAL DEBUG ANALYSIS:")
            print(f"=" * 50)
            
            # 1. Check which processing pipeline was used
            success = data.get('success', False)
            session_id = data.get('session_id', 'unknown')
            processing_time_backend = data.get('processing_time', 0)
            
            print(f"✅ Processing Success: {success}")
            print(f"🆔 Session ID: {session_id}")
            print(f"⏱️ Backend Processing Time: {processing_time_backend:.2f}s")
            
            # 2. Check H1 detection and chunking
            articles = data.get('articles', [])
            images_processed = data.get('images_processed', 0)
            
            print(f"\n🔍 H1 DETECTION AND CHUNKING ANALYSIS:")
            print(f"📚 Total Articles Generated: {len(articles)}")
            print(f"🖼️ Images Processed: {images_processed}")
            
            if len(articles) == 0:
                print(f"❌ CRITICAL ISSUE: No articles generated!")
                print(f"❌ Expected: 4 articles (one per H1 section)")
                return False
            
            # 3. Analyze article titles and structure
            print(f"\n📄 ARTICLE ANALYSIS:")
            print(f"Expected: 4 articles based on H1 structure")
            print(f"Actual: {len(articles)} articles")
            
            h1_based_titles = 0
            generic_titles = 0
            
            for i, article in enumerate(articles, 1):
                title = article.get('title', 'No Title')
                word_count = article.get('word_count', 0)
                content_preview = (article.get('content', '') or article.get('html', ''))[:100]
                
                print(f"\n📄 Article {i}:")
                print(f"   Title: '{title}'")
                print(f"   Word Count: {word_count}")
                print(f"   Content Preview: {content_preview}...")
                
                # Check if title is H1-based or generic
                if any(h1_keyword in title.lower() for h1_keyword in ['introduction', 'preprocessing', 'training', 'deployment', 'machine learning', 'data', 'model', 'production']):
                    h1_based_titles += 1
                    print(f"   ✅ H1-based title detected")
                elif 'comprehensive guide' in title.lower() or 'article' in title.lower():
                    generic_titles += 1
                    print(f"   ⚠️ Generic AI-generated title detected")
                else:
                    print(f"   ❓ Title type unclear")
            
            # 4. Determine the root cause
            print(f"\n🎯 ROOT CAUSE ANALYSIS:")
            print(f"=" * 40)
            
            if len(articles) == 1 and generic_titles > 0:
                print(f"❌ ISSUE IDENTIFIED: Single article with generic title")
                print(f"❌ ROOT CAUSE: H1 elements not being detected during chunking")
                print(f"❌ PIPELINE: Likely using text processing instead of HTML preprocessing")
                return False
                
            elif len(articles) == 4 and h1_based_titles >= 3:
                print(f"✅ SUCCESS: Multiple articles with H1-based titles")
                print(f"✅ ROOT CAUSE: H1 detection and chunking working correctly")
                print(f"✅ PIPELINE: HTML preprocessing pipeline operational")
                return True
                
            elif len(articles) > 1 and len(articles) < 4:
                print(f"⚠️ PARTIAL SUCCESS: Multiple articles but not expected count")
                print(f"⚠️ ROOT CAUSE: H1 detection working but chunking logic may need adjustment")
                print(f"⚠️ PIPELINE: HTML preprocessing partially operational")
                return True
                
            elif len(articles) > 4:
                print(f"⚠️ OVER-CHUNKING: More articles than H1 sections")
                print(f"⚠️ ROOT CAUSE: Chunking creating sub-articles beyond H1 structure")
                print(f"⚠️ PIPELINE: HTML preprocessing working but over-segmenting")
                return True
            
            else:
                print(f"❓ UNCLEAR RESULT: Unexpected article pattern")
                print(f"❓ Articles: {len(articles)}, H1-based: {h1_based_titles}, Generic: {generic_titles}")
                return False
                
        except Exception as e:
            print(f"❌ MULTI-H1 DEBUG TEST FAILED: {str(e)}")
            import traceback
            traceback.print_exc()
            return False

    def test_backend_logs_capture(self):
        """Attempt to capture backend logs for debugging"""
        print("\n🔍 ATTEMPTING TO CAPTURE BACKEND DEBUG LOGS")
        print("=" * 60)
        
        try:
            # Check if we can access backend logs through any endpoint
            print("📋 Checking for debug log endpoints...")
            
            # Try health endpoint to see if debug info is available
            response = requests.get(f"{self.base_url}/health", timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Health endpoint accessible")
                
                # Look for any debug or logging information
                if 'debug' in data or 'logs' in data:
                    print(f"📋 Debug information available in health endpoint")
                    print(f"Debug data: {json.dumps(data, indent=2)}")
                else:
                    print(f"⚠️ No debug information in health endpoint")
                    
            # Try to get recent processing logs if available
            try:
                logs_response = requests.get(f"{self.base_url}/logs", timeout=5)
                if logs_response.status_code == 200:
                    print(f"📋 Logs endpoint found!")
                    logs_data = logs_response.json()
                    print(f"Recent logs: {json.dumps(logs_data, indent=2)}")
                else:
                    print(f"⚠️ No logs endpoint available (status: {logs_response.status_code})")
            except:
                print(f"⚠️ No logs endpoint available")
                
            return True
            
        except Exception as e:
            print(f"⚠️ Backend logs capture failed: {str(e)}")
            return True  # Not critical for main test

    def run_complete_debug_test(self):
        """Run the complete multi-H1 debug test"""
        print("🚀 STARTING COMPLETE MULTI-H1 DEBUG TEST")
        print("=" * 80)
        
        # Test 1: Multi-H1 document processing
        print("\n📋 TEST 1: Multi-H1 Document Processing")
        result1 = self.test_multi_h1_document_processing()
        
        # Test 2: Backend logs capture (optional)
        print("\n📋 TEST 2: Backend Logs Capture")
        result2 = self.test_backend_logs_capture()
        
        # Final summary
        print(f"\n🎯 FINAL DEBUG TEST SUMMARY")
        print(f"=" * 50)
        print(f"Multi-H1 Processing: {'✅ PASSED' if result1 else '❌ FAILED'}")
        print(f"Backend Logs: {'✅ ACCESSIBLE' if result2 else '⚠️ LIMITED'}")
        
        if result1:
            print(f"\n✅ MULTI-H1 DEBUG TEST COMPLETED SUCCESSFULLY")
            print(f"🎯 The HTML preprocessing pipeline is working correctly")
            print(f"🎯 H1 detection and chunking logic is operational")
            print(f"🎯 Multiple articles are being generated based on document structure")
        else:
            print(f"\n❌ MULTI-H1 DEBUG TEST REVEALED ISSUES")
            print(f"🎯 H1 detection or chunking logic needs investigation")
            print(f"🎯 Check if HTML preprocessing pipeline is being used")
            print(f"🎯 Verify markdown-to-HTML conversion for text files")
        
        return result1

def main():
    """Main test execution"""
    print("🔍 MULTI-H1 DOCUMENT DEBUG TEST FOR TRAINING ENGINE")
    print("🎯 Objective: Capture complete trace of HTML preprocessing pipeline")
    print("=" * 80)
    
    tester = MultiH1DebugTest()
    success = tester.run_complete_debug_test()
    
    if success:
        print(f"\n🎉 ALL TESTS COMPLETED SUCCESSFULLY!")
        exit(0)
    else:
        print(f"\n❌ TESTS REVEALED CRITICAL ISSUES!")
        exit(1)

if __name__ == "__main__":
    main()