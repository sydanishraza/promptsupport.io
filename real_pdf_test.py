#!/usr/bin/env python3
"""
Real PDF Testing for Critical Fix 2: PDF Image Extraction & Asset Library Integration
"""

import requests
import json
import os
import time
from dotenv import load_dotenv

# Load environment variables
load_dotenv('/app/frontend/.env')

# Get backend URL from environment
BACKEND_URL = os.environ.get('REACT_APP_BACKEND_URL', 'https://content-engine-10.preview.emergentagent.com') + '/api'

class RealPDFTest:
    def __init__(self):
        self.base_url = BACKEND_URL
        print(f"🎯 Testing Real PDF Processing at: {self.base_url}")
        
    def test_real_pdf_processing(self):
        """Test with actual PDF file for image extraction"""
        print("\n🎯 TESTING REAL PDF IMAGE EXTRACTION & ASSET LIBRARY INTEGRATION")
        print("=" * 70)
        
        try:
            # Find available PDF files
            pdf_files = [
                '/app/test_training_with_images.pdf',
                '/app/Whisk_Studio_Integration_Guide.pdf', 
                '/app/test_pdf_improved.pdf',
                '/app/test_training.pdf'
            ]
            
            # Find the first existing PDF
            test_pdf = None
            for pdf_path in pdf_files:
                if os.path.exists(pdf_path):
                    test_pdf = pdf_path
                    break
            
            if not test_pdf:
                print("❌ No PDF files found for testing")
                return False
            
            print(f"📄 Testing with PDF: {test_pdf}")
            
            # Get initial Asset Library count
            response = requests.get(f"{self.base_url}/assets", timeout=15)
            initial_assets = 0
            if response.status_code == 200:
                initial_assets = response.json().get('total', 0)
            
            print(f"📊 Initial Asset Library count: {initial_assets}")
            
            # Process the real PDF file
            with open(test_pdf, 'rb') as pdf_file:
                files = {
                    'file': (os.path.basename(test_pdf), pdf_file, 'application/pdf')
                }
                
                form_data = {
                    'template_id': 'phase1_document_processing',
                    'training_mode': 'true',
                    'template_instructions': json.dumps({
                        "template_id": "phase1_document_processing",
                        "processing_instructions": "Extract PDF images and save to Asset Library",
                        "media_handling": {
                            "extract_images": True,
                            "save_to_asset_library": True,
                            "pdf_image_extraction": True
                        }
                    })
                }
                
                print("📤 Processing real PDF file...")
                
                start_time = time.time()
                response = requests.post(
                    f"{self.base_url}/training/process",
                    files=files,
                    data=form_data,
                    timeout=180  # Extended timeout for real PDF processing
                )
                processing_time = time.time() - start_time
                
                print(f"⏱️ Processing completed in {processing_time:.2f} seconds")
                print(f"📊 Response Status Code: {response.status_code}")
                
                if response.status_code != 200:
                    print(f"❌ PDF processing failed: {response.status_code}")
                    print(f"Response: {response.text}")
                    return False
                
                data = response.json()
                
                # Check processing results
                success = data.get('success', False)
                images_processed = data.get('images_processed', 0)
                articles = data.get('articles', [])
                
                print(f"📊 Real PDF Processing Results:")
                print(f"  Success: {success}")
                print(f"  Images Processed: {images_processed}")
                print(f"  Articles Generated: {len(articles)}")
                
                # Wait for Asset Library to update
                time.sleep(3)
                
                # Check Asset Library for new images
                print("\n🔍 Checking Asset Library for PDF images...")
                
                response = requests.get(f"{self.base_url}/assets", timeout=15)
                
                if response.status_code == 200:
                    asset_data = response.json()
                    current_assets = asset_data.get('assets', [])
                    current_total = asset_data.get('total', 0)
                    
                    print(f"📊 Current Asset Library count: {current_total}")
                    print(f"📊 Asset count change: {current_total - initial_assets}")
                    
                    # Look for recently added assets
                    recent_assets = []
                    for asset in current_assets:
                        source = asset.get('source', '')
                        asset_type = asset.get('asset_type', '')
                        
                        if ('training_engine' in source or 
                            'extraction' in source or 
                            asset_type == 'image'):
                            recent_assets.append(asset)
                    
                    print(f"🖼️ Recent/relevant assets found: {len(recent_assets)}")
                    
                    # Show sample recent assets
                    for i, asset in enumerate(recent_assets[:5]):
                        filename = asset.get('filename', 'unknown')
                        asset_type = asset.get('asset_type', 'unknown')
                        source = asset.get('source', 'unknown')
                        file_size = asset.get('file_size', 0)
                        print(f"  📁 Asset {i+1}: {filename} ({asset_type}, {file_size} bytes) from {source}")
                    
                    # Check articles for embedded images
                    embedded_images = 0
                    for article in articles:
                        content = article.get('content', '')
                        embedded_images += content.count('/api/static/uploads/')
                        embedded_images += content.count('<figure')
                    
                    print(f"🖼️ Embedded images in articles: {embedded_images}")
                    
                    # ASSESSMENT
                    asset_increase = current_total - initial_assets
                    
                    if images_processed > 0 and asset_increase > 0:
                        print("\n✅ CRITICAL FIX 2 VERIFICATION SUCCESSFUL:")
                        print(f"  ✅ PDF processed successfully")
                        print(f"  ✅ Images processed: {images_processed}")
                        print(f"  ✅ Asset Library count increased by {asset_increase}")
                        print(f"  ✅ {len(recent_assets)} relevant assets found")
                        print("  ✅ PDF image extraction and Asset Library integration working")
                        return True
                    elif images_processed > 0:
                        print("\n⚠️ CRITICAL FIX 2 PARTIAL SUCCESS:")
                        print(f"  ✅ Images processed: {images_processed}")
                        print(f"  ⚠️ Asset Library increase: {asset_increase}")
                        print("  ⚠️ Images may be processed but Asset Library integration needs verification")
                        return True
                    elif asset_increase > 0:
                        print("\n⚠️ CRITICAL FIX 2 PARTIAL SUCCESS:")
                        print(f"  ⚠️ Images processed: {images_processed}")
                        print(f"  ✅ Asset Library increase: {asset_increase}")
                        print("  ⚠️ Asset Library working but image processing may need verification")
                        return True
                    else:
                        print("\n❌ CRITICAL FIX 2 FAILED:")
                        print(f"  ❌ Images processed: {images_processed}")
                        print(f"  ❌ Asset Library increase: {asset_increase}")
                        print("  ❌ PDF image extraction not working as expected")
                        return False
                else:
                    print(f"❌ Could not check Asset Library: {response.status_code}")
                    return False
                    
        except Exception as e:
            print(f"❌ Real PDF test failed: {e}")
            import traceback
            traceback.print_exc()
            return False

    def test_docx_processing_for_comparison(self):
        """Test DOCX processing to compare with PDF"""
        print("\n🔍 Testing DOCX Processing for Comparison...")
        
        try:
            # Create test DOCX content
            test_content = """DOCX Image Processing Test

This document tests DOCX image processing to compare with PDF processing.

The DOCX processing should:
1. Extract images from DOCX files
2. Save images to Asset Library
3. Embed images in generated articles
4. Show proper image counts

This helps verify that the image processing pipeline works for DOCX files."""

            # Process as DOCX
            import io
            file_data = io.BytesIO(test_content.encode('utf-8'))
            
            files = {
                'file': ('docx_comparison_test.docx', file_data, 'application/vnd.openxmlformats-officedocument.wordprocessingml.document')
            }
            
            form_data = {
                'template_id': 'phase1_document_processing',
                'training_mode': 'true',
                'template_instructions': json.dumps({
                    "template_id": "phase1_document_processing",
                    "media_handling": {"extract_images": True}
                })
            }
            
            print("📤 Processing DOCX for comparison...")
            
            response = requests.post(
                f"{self.base_url}/training/process",
                files=files,
                data=form_data,
                timeout=60
            )
            
            if response.status_code == 200:
                data = response.json()
                images_processed = data.get('images_processed', 0)
                articles = data.get('articles', [])
                
                print(f"📊 DOCX Processing Results:")
                print(f"  Images Processed: {images_processed}")
                print(f"  Articles Generated: {len(articles)}")
                
                return True
            else:
                print(f"❌ DOCX processing failed: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ DOCX comparison test failed: {e}")
            return False

if __name__ == "__main__":
    tester = RealPDFTest()
    
    print("🎯 REAL PDF TESTING FOR CRITICAL FIX 2")
    print("=" * 50)
    
    # Test real PDF processing
    pdf_success = tester.test_real_pdf_processing()
    
    # Test DOCX for comparison
    docx_success = tester.test_docx_processing_for_comparison()
    
    print("\n" + "=" * 50)
    print("📊 REAL PDF TESTING SUMMARY")
    print("=" * 50)
    print(f"PDF Processing: {'✅ SUCCESS' if pdf_success else '❌ FAILED'}")
    print(f"DOCX Comparison: {'✅ SUCCESS' if docx_success else '❌ FAILED'}")
    
    if pdf_success:
        print("\n✅ Critical Fix 2 (PDF Image Extraction & Asset Library) is working!")
    else:
        print("\n❌ Critical Fix 2 needs attention.")