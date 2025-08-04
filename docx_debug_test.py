#!/usr/bin/env python3
"""
DOCX Multi-H1 Debug Test - Trigger HTML Preprocessing Pipeline
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
BACKEND_URL = os.environ.get('REACT_APP_BACKEND_URL', 'https://404d0371-ecd8-49d3-b3e6-1bf697a10fe7.preview.emergentagent.com') + '/api'

def test_docx_html_pipeline():
    """Test with DOCX file to trigger HTML preprocessing pipeline"""
    print("🔍 TESTING DOCX FILE TO TRIGGER HTML PREPROCESSING PIPELINE")
    print("=" * 70)
    
    # Create DOCX-like content (will be treated as DOCX due to extension)
    docx_content = """<h1>Introduction to Machine Learning</h1>
<p>This is the introduction section that explains the basics of machine learning and artificial intelligence. This section should become the first article based on the H1 heading structure.</p>
<p>Machine learning is a subset of artificial intelligence that enables computers to learn and make decisions from data without being explicitly programmed for every task.</p>

<h1>Data Preprocessing and Feature Engineering</h1>
<p>This is the second major section focusing on data preprocessing techniques. This should become the second article based on the H1 heading structure.</p>
<p>Data preprocessing is crucial for successful machine learning projects. It involves cleaning, transforming, and preparing raw data for analysis.</p>

<h1>Model Training and Evaluation</h1>
<p>This is the third major section covering model training methodologies. This should become the third article based on the H1 heading structure.</p>
<p>Model training involves selecting appropriate algorithms, tuning hyperparameters, and evaluating model performance using various metrics.</p>

<h1>Deployment and Production Considerations</h1>
<p>This is the fourth and final major section about deploying models to production. This should become the fourth article based on the H1 heading structure.</p>
<p>Deploying machine learning models to production requires careful consideration of scalability, monitoring, and maintenance requirements.</p>"""

    try:
        file_data = io.BytesIO(docx_content.encode('utf-8'))
        
        files = {
            'file': ('multi_h1_test.docx', file_data, 'application/vnd.openxmlformats-officedocument.wordprocessingml.document')
        }
        
        form_data = {
            'template_id': 'phase1_document_processing',
            'training_mode': 'true'
        }
        
        print("📤 Uploading DOCX file to trigger HTML preprocessing pipeline...")
        
        start_time = time.time()
        response = requests.post(
            f"{BACKEND_URL}/training/process",
            files=files,
            data=form_data,
            timeout=120
        )
        processing_time = time.time() - start_time
        
        print(f"⏱️ Processing completed in {processing_time:.2f} seconds")
        print(f"📊 Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            articles = data.get('articles', [])
            
            print(f"\n🔍 DOCX PROCESSING RESULTS:")
            print(f"Articles Generated: {len(articles)}")
            
            for i, article in enumerate(articles, 1):
                title = article.get('title', 'No Title')
                print(f"Article {i}: '{title}'")
            
            return True
        else:
            print(f"❌ DOCX processing failed: {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ DOCX test failed: {str(e)}")
        return False

if __name__ == "__main__":
    test_docx_html_pipeline()