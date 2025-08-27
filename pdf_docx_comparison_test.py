#!/usr/bin/env python3
"""
PDF vs DOCX Processing Comparison Test
Compare processing paths between PDF and DOCX to identify differences
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
BACKEND_URL = os.environ.get('REACT_APP_BACKEND_URL', 'https://content-engine-10.preview.emergentagent.com') + '/api'

def test_pdf_vs_docx_processing():
    """
    Compare PDF and DOCX processing to identify differences in processing paths
    """
    print("🔍 PDF vs DOCX PROCESSING COMPARISON")
    print("="*80)
    print("OBJECTIVE: Compare processing paths between PDF and DOCX")
    print("EXPECTED: Both should use comprehensive processing")
    print("="*80)
    
    # Test identical content with both formats
    test_content = """Processing Comparison Test Document

# Section A: Data Analysis Methods
This section covers comprehensive data analysis methods including statistical analysis, data visualization, and predictive modeling techniques. Organizations need robust analytical frameworks to extract meaningful insights from complex datasets and drive data-driven decision making processes.

# Section B: Implementation Strategies  
This section focuses on practical implementation strategies for data-driven decision making in business environments. Companies must develop systematic approaches to integrate analytical insights into operational workflows and strategic planning processes.

# Section C: Performance Metrics
This section outlines key performance metrics and measurement frameworks for evaluating data analysis effectiveness. Proper measurement systems enable organizations to assess the impact of analytical initiatives and optimize their data science investments."""

    results = {}
    
    # Test DOCX processing
    print("\n📤 Testing DOCX processing...")
    docx_file_data = io.BytesIO(test_content.encode('utf-8'))
    
    docx_files = {
        'file': ('comparison_test.docx', docx_file_data, 'application/vnd.openxmlformats-officedocument.wordprocessingml.document')
    }
    
    docx_form_data = {
        'template_id': 'comprehensive_processing',
        'training_mode': 'true'
    }
    
    try:
        docx_start = time.time()
        docx_response = requests.post(
            f"{BACKEND_URL}/training/process",
            files=docx_files,
            data=docx_form_data,
            timeout=120
        )
        docx_time = time.time() - docx_start
        
        if docx_response.status_code == 200:
            docx_data = docx_response.json()
            docx_articles = docx_data.get('articles', [])
            
            results['docx'] = {
                'success': True,
                'articles_count': len(docx_articles),
                'processing_time': docx_time,
                'articles': docx_articles,
                'processing_approach': docx_data.get('processing_approach', 'unknown'),
                'response_keys': list(docx_data.keys())
            }
            
            print(f"✅ DOCX Processing: {len(docx_articles)} articles in {docx_time:.2f}s")
        else:
            results['docx'] = {'success': False, 'error': f"Status {docx_response.status_code}"}
            print(f"❌ DOCX Processing failed: {docx_response.status_code}")
            
    except Exception as e:
        results['docx'] = {'success': False, 'error': str(e)}
        print(f"❌ DOCX Processing error: {e}")
    
    # Test PDF processing (simulate with text file marked as PDF)
    print("\n📤 Testing PDF processing...")
    pdf_file_data = io.BytesIO(test_content.encode('utf-8'))
    
    pdf_files = {
        'file': ('comparison_test.pdf', pdf_file_data, 'application/pdf')
    }
    
    pdf_form_data = {
        'template_id': 'comprehensive_processing',
        'training_mode': 'true'
    }
    
    try:
        pdf_start = time.time()
        pdf_response = requests.post(
            f"{BACKEND_URL}/training/process",
            files=pdf_files,
            data=pdf_form_data,
            timeout=120
        )
        pdf_time = time.time() - pdf_start
        
        if pdf_response.status_code == 200:
            pdf_data = pdf_response.json()
            pdf_articles = pdf_data.get('articles', [])
            
            results['pdf'] = {
                'success': True,
                'articles_count': len(pdf_articles),
                'processing_time': pdf_time,
                'articles': pdf_articles,
                'processing_approach': pdf_data.get('processing_approach', 'unknown'),
                'response_keys': list(pdf_data.keys())
            }
            
            print(f"✅ PDF Processing: {len(pdf_articles)} articles in {pdf_time:.2f}s")
        else:
            results['pdf'] = {'success': False, 'error': f"Status {pdf_response.status_code}"}
            print(f"❌ PDF Processing failed: {pdf_response.status_code}")
            
    except Exception as e:
        results['pdf'] = {'success': False, 'error': str(e)}
        print(f"❌ PDF Processing error: {e}")
    
    # Compare results
    print(f"\n📊 DETAILED COMPARISON RESULTS:")
    print("="*60)
    
    if results.get('docx', {}).get('success') and results.get('pdf', {}).get('success'):
        docx_data = results['docx']
        pdf_data = results['pdf']
        
        print(f"📚 Article Count Comparison:")
        print(f"  DOCX Articles: {docx_data['articles_count']}")
        print(f"  PDF Articles: {pdf_data['articles_count']}")
        
        print(f"\n⏱️ Processing Time Comparison:")
        print(f"  DOCX Time: {docx_data['processing_time']:.2f}s")
        print(f"  PDF Time: {pdf_data['processing_time']:.2f}s")
        
        print(f"\n🔧 Processing Approach Comparison:")
        print(f"  DOCX Approach: {docx_data['processing_approach']}")
        print(f"  PDF Approach: {pdf_data['processing_approach']}")
        
        print(f"\n📋 Response Keys Comparison:")
        print(f"  DOCX Keys: {docx_data['response_keys']}")
        print(f"  PDF Keys: {pdf_data['response_keys']}")
        
        # Compare article characteristics
        print(f"\n📄 Article Quality Comparison:")
        
        # DOCX article analysis
        docx_total_words = 0
        for i, article in enumerate(docx_data['articles']):
            content = article.get('content', '') or article.get('html', '')
            word_count = len(content.split()) if content else 0
            docx_total_words += word_count
            title = article.get('title', 'Untitled')
            print(f"  DOCX Article {i+1}: '{title}' ({word_count} words)")
        
        docx_avg_words = docx_total_words / docx_data['articles_count'] if docx_data['articles_count'] > 0 else 0
        
        # PDF article analysis
        pdf_total_words = 0
        for i, article in enumerate(pdf_data['articles']):
            content = article.get('content', '') or article.get('html', '')
            word_count = len(content.split()) if content else 0
            pdf_total_words += word_count
            title = article.get('title', 'Untitled')
            print(f"  PDF Article {i+1}: '{title}' ({word_count} words)")
        
        pdf_avg_words = pdf_total_words / pdf_data['articles_count'] if pdf_data['articles_count'] > 0 else 0
        
        print(f"\n📈 Word Count Analysis:")
        print(f"  DOCX Average: {docx_avg_words:.0f} words per article")
        print(f"  PDF Average: {pdf_avg_words:.0f} words per article")
        print(f"  Expected: 800-1500 words per article")
        
        # Root cause analysis
        print(f"\n🔍 ROOT CAUSE ANALYSIS:")
        
        if docx_data['articles_count'] < pdf_data['articles_count']:
            print("❌ DOCX PROCESSING ISSUE DETECTED:")
            print("  - DOCX generates fewer articles than PDF")
            print("  - DOCX may be using simplified processing")
            return False
        elif docx_avg_words < pdf_avg_words * 0.8:
            print("❌ DOCX CONTENT QUALITY ISSUE:")
            print("  - DOCX articles are significantly shorter than PDF")
            print("  - DOCX may not be using comprehensive processing")
            return False
        elif docx_avg_words < 800 and pdf_avg_words < 800:
            print("❌ BOTH FORMATS USING SIMPLIFIED PROCESSING:")
            print("  - Both DOCX and PDF articles are too short")
            print("  - Neither format is using comprehensive processing")
            return False
        elif docx_avg_words < 800:
            print("❌ DOCX SPECIFIC ISSUE:")
            print("  - DOCX articles are too short (< 800 words)")
            print("  - PDF processing works better than DOCX")
            return False
        else:
            print("✅ DOCX AND PDF PROCESSING COMPARABLE:")
            print("  - Similar article counts and word counts")
            print("  - Both using comprehensive processing")
            return True
    else:
        print("❌ Comparison failed - one or both formats failed to process")
        if not results.get('docx', {}).get('success'):
            print(f"  DOCX Error: {results.get('docx', {}).get('error', 'Unknown')}")
        if not results.get('pdf', {}).get('success'):
            print(f"  PDF Error: {results.get('pdf', {}).get('error', 'Unknown')}")
        return False

def main():
    """Run the PDF vs DOCX comparison test"""
    print("🎯 PDF vs DOCX PROCESSING COMPARISON TEST")
    print("Comparing processing paths to identify why DOCX generates")
    print("single summarized articles instead of comprehensive ones")
    
    success = test_pdf_vs_docx_processing()
    
    if success:
        print(f"\n✅ COMPARISON COMPLETED - DOCX and PDF processing are comparable")
    else:
        print(f"\n❌ COMPARISON COMPLETED - DOCX processing has issues compared to PDF")
    
    return success

if __name__ == "__main__":
    main()