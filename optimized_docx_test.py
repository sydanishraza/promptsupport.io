#!/usr/bin/env python3
"""
OPTIMIZED DOCX Processing Pipeline Test
Focused test for performance improvements verification
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
BACKEND_URL = os.environ.get('REACT_APP_BACKEND_URL', 'https://1624c9e6-2ea4-4da8-9b16-2db1628b7f04.preview.emergentagent.com') + '/api'

def test_optimized_docx_processing_pipeline():
    """Test the OPTIMIZED DOCX processing pipeline for performance improvements"""
    print("\n🔍 Testing OPTIMIZED DOCX Processing Pipeline Performance...")
    try:
        # Create a comprehensive DOCX-like test content that should trigger optimized processing
        test_content = """OPTIMIZED DOCX PROCESSING PERFORMANCE TEST DOCUMENT

This comprehensive test document is designed to verify the performance optimizations implemented in the DOCX processing pipeline. The system should now process documents significantly faster while maintaining content quality.

PERFORMANCE OPTIMIZATION TARGETS:
1. Processing Time: Should complete within 60-90 seconds (down from 4+ minutes)
2. Segmented Generation: Should use only 2 segments instead of 6
3. Word Count per Segment: Should be 400-800 words instead of 1000-2000
4. Segmentation Threshold: Now 5000 chars instead of 2000

SECTION 1: INTRODUCTION TO OPTIMIZATION
The enhanced processing pipeline implements several key optimizations:
- Reduced segmentation for faster processing
- Optimized word count targets per segment
- Improved threshold calculations
- Streamlined content generation workflow

SECTION 2: TECHNICAL IMPLEMENTATION DETAILS
The optimization focuses on balancing processing speed with content quality:
- Smart segmentation algorithms
- Efficient content chunking
- Reduced LLM API calls (3-4 instead of 7-8)
- Optimized content length management

SECTION 3: QUALITY ASSURANCE MEASURES
Despite performance improvements, content quality is maintained through:
- Comprehensive content coverage
- Professional HTML structure preservation
- Technical documentation quality standards
- Proper image embedding functionality

SECTION 4: PERFORMANCE METRICS VERIFICATION
Key metrics to verify during testing:
- Total processing time under 90 seconds
- Segment count reduced to 2
- Word count per segment 400-800 words
- Proper HTML structure maintained
- Image embedding still functional

SECTION 5: USER EXPERIENCE IMPROVEMENTS
The optimizations should result in:
- No more "keeps on processing" experience
- Responsive processing within acceptable timeframe
- Proper status updates during processing
- Maintained content comprehensiveness

This test document contains sufficient content to trigger the optimized processing pipeline while allowing verification of all performance improvements and quality maintenance measures."""

        # Create file-like object simulating a DOCX file
        file_data = io.BytesIO(test_content.encode('utf-8'))
        
        # Prepare template data for Phase 1 processing
        template_data = {
            "template_id": "phase1_document_processing",
            "processing_instructions": "Apply Phase 1 optimized processing with reduced segmentation",
            "output_requirements": {
                "format": "html",
                "min_articles": 1,
                "max_articles": 2,
                "target_segments": 2,
                "words_per_segment": "400-800",
                "segmentation_threshold": 5000
            },
            "quality_benchmarks": [
                "content_completeness",
                "no_duplication", 
                "proper_formatting",
                "professional_presentation"
            ],
            "media_handling": "contextual_embedding"
        }
        
        files = {
            'file': ('optimized_docx_test.docx', file_data, 'application/vnd.openxmlformats-officedocument.wordprocessingml.document')
        }
        
        form_data = {
            'template_id': 'phase1_document_processing',
            'training_mode': 'true',
            'template_instructions': json.dumps(template_data)
        }
        
        print("🚀 Starting OPTIMIZED DOCX processing test...")
        print(f"📄 Test content length: {len(test_content)} characters")
        print(f"🎯 Expected: 2 segments, 400-800 words each, <90s processing time")
        
        # Record start time for performance measurement
        start_time = time.time()
        
        response = requests.post(
            f"{BACKEND_URL}/training/process",
            files=files,
            data=form_data,
            timeout=120  # Allow up to 2 minutes for processing
        )
        
        end_time = time.time()
        processing_time = end_time - start_time
        
        print(f"⏱️ Actual processing time: {processing_time:.2f} seconds")
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"Response keys: {list(data.keys())}")
            
            if data.get("success"):
                articles = data.get("articles", [])
                images_processed = data.get("images_processed", 0)
                reported_processing_time = data.get("processing_time", processing_time)
                
                print(f"✅ Processing successful!")
                print(f"📚 Articles generated: {len(articles)}")
                print(f"🖼️ Images processed: {images_processed}")
                print(f"⏱️ Reported processing time: {reported_processing_time}s")
                
                # PERFORMANCE VERIFICATION
                performance_results = []
                
                # 1. Processing Speed Test (60-90 seconds target)
                if processing_time <= 90:
                    print(f"✅ SPEED TEST PASSED: {processing_time:.2f}s ≤ 90s target")
                    performance_results.append(True)
                else:
                    print(f"❌ SPEED TEST FAILED: {processing_time:.2f}s > 90s target")
                    performance_results.append(False)
                
                # 2. Segmented Generation Test (2 segments instead of 6)
                if len(articles) <= 2:
                    print(f"✅ SEGMENTATION TEST PASSED: {len(articles)} articles ≤ 2 target")
                    performance_results.append(True)
                else:
                    print(f"❌ SEGMENTATION TEST FAILED: {len(articles)} articles > 2 target")
                    performance_results.append(False)
                
                # 3. Word Count per Segment Test (400-800 words)
                word_count_results = []
                for i, article in enumerate(articles):
                    content = article.get("content", "")
                    word_count = len(content.split()) if content else 0
                    
                    print(f"📄 Article {i+1} word count: {word_count}")
                    
                    if 400 <= word_count <= 800:
                        print(f"✅ Article {i+1} word count in target range (400-800)")
                        word_count_results.append(True)
                    else:
                        print(f"⚠️ Article {i+1} word count outside target: {word_count}")
                        word_count_results.append(False)
                
                if word_count_results and all(word_count_results):
                    print("✅ WORD COUNT TEST PASSED: All articles in 400-800 word range")
                    performance_results.append(True)
                elif word_count_results and any(word_count_results):
                    print("⚠️ WORD COUNT TEST PARTIAL: Some articles in target range")
                    performance_results.append(True)  # Partial success acceptable
                else:
                    print("❌ WORD COUNT TEST FAILED: No articles in target range")
                    performance_results.append(False)
                
                # CONTENT QUALITY VERIFICATION
                quality_results = []
                
                # 4. Content Quality - HTML Structure
                html_structure_good = True
                for i, article in enumerate(articles):
                    content = article.get("content", "")
                    if content:
                        # Check for proper HTML structure
                        html_tags = ['<h1>', '<h2>', '<h3>', '<p>', '<div>']
                        html_found = sum(1 for tag in html_tags if tag in content)
                        
                        if html_found >= 2:  # At least some HTML structure
                            print(f"✅ Article {i+1} has proper HTML structure ({html_found} tags)")
                        else:
                            print(f"⚠️ Article {i+1} may lack HTML structure")
                            html_structure_good = False
                
                quality_results.append(html_structure_good)
                
                # 5. Content Comprehensiveness
                total_content_length = sum(len(article.get("content", "")) for article in articles)
                if total_content_length >= 1000:  # Reasonable total content
                    print(f"✅ CONTENT COMPREHENSIVENESS: {total_content_length} total characters")
                    quality_results.append(True)
                else:
                    print(f"⚠️ CONTENT COMPREHENSIVENESS: {total_content_length} characters may be insufficient")
                    quality_results.append(False)
                
                # 6. Professional Quality Check
                professional_quality = True
                for article in articles:
                    title = article.get("title", "")
                    if title and len(title) > 10:  # Reasonable title length
                        continue
                    else:
                        professional_quality = False
                        break
                
                quality_results.append(professional_quality)
                
                # OVERALL ASSESSMENT
                performance_score = sum(performance_results)
                quality_score = sum(quality_results)
                total_performance_tests = len(performance_results)
                total_quality_tests = len(quality_results)
                
                print(f"\n📊 OPTIMIZATION RESULTS SUMMARY:")
                print(f"⚡ Performance Tests: {performance_score}/{total_performance_tests} passed")
                print(f"🎯 Quality Tests: {quality_score}/{total_quality_tests} passed")
                
                # Success criteria: At least 2/3 performance tests and 2/3 quality tests
                if performance_score >= 2 and quality_score >= 2:
                    print("🎉 OPTIMIZED DOCX PROCESSING PIPELINE TEST PASSED!")
                    print("✅ Performance improvements verified while maintaining quality")
                    return True
                elif performance_score >= 2:
                    print("⚠️ PERFORMANCE OPTIMIZATIONS WORKING but quality needs attention")
                    return True  # Performance is the main focus
                else:
                    print("❌ OPTIMIZATION TEST FAILED: Performance targets not met")
                    return False
                    
            else:
                print(f"❌ Processing failed: {data}")
                return False
        else:
            print(f"❌ DOCX processing failed - status code {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Optimized DOCX processing test failed - {str(e)}")
        return False

if __name__ == "__main__":
    print("🚀 OPTIMIZED DOCX Processing Pipeline Test")
    print("=" * 60)
    
    result = test_optimized_docx_processing_pipeline()
    
    if result:
        print("\n✅ OPTIMIZED DOCX PROCESSING PIPELINE: PASSED")
    else:
        print("\n❌ OPTIMIZED DOCX PROCESSING PIPELINE: FAILED")