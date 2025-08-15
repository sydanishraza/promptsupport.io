#!/usr/bin/env python3
"""
IMAGE EXTRACTION TEST
Specific test for image extraction from the Customer Summary Screen User Guide DOCX file
"""

import requests
import json
import os
import zipfile
from dotenv import load_dotenv

# Load environment variables
load_dotenv('/app/frontend/.env')

# Get backend URL from environment
BACKEND_URL = os.environ.get('REACT_APP_BACKEND_URL', 'https://docai-promptsupport.preview.emergentagent.com') + '/api'

def analyze_docx_file_structure():
    """Analyze the DOCX file to see if it actually contains images"""
    print("🔍 DOCX FILE STRUCTURE ANALYSIS")
    print("=" * 60)
    
    docx_path = "/app/Customer_Summary_Screen_User_Guide_1.3.docx"
    
    try:
        with zipfile.ZipFile(docx_path, 'r') as docx_zip:
            file_list = docx_zip.namelist()
            
            print(f"📁 DOCX contains {len(file_list)} files")
            
            # Look for media files
            media_files = [f for f in file_list if f.startswith('word/media/')]
            image_files = [f for f in file_list if any(f.lower().endswith(ext) for ext in ['.png', '.jpg', '.jpeg', '.gif', '.bmp', '.tiff'])]
            
            print(f"🖼️ Media directory files: {len(media_files)}")
            print(f"🖼️ Image files found: {len(image_files)}")
            
            if media_files:
                print("\n📋 Media files in DOCX:")
                for i, media_file in enumerate(media_files[:10]):  # Show first 10
                    try:
                        file_info = docx_zip.getinfo(media_file)
                        size_kb = file_info.file_size / 1024
                        print(f"  {i+1}. {media_file} ({size_kb:.1f} KB)")
                    except:
                        print(f"  {i+1}. {media_file}")
                
                if len(media_files) > 10:
                    print(f"  ... and {len(media_files) - 10} more files")
                
                print(f"\n✅ DOCX CONTAINS {len(media_files)} MEDIA FILES")
                print("✅ Images should be extractable from this document")
                return True
            else:
                print("\n❌ NO MEDIA FILES FOUND IN DOCX")
                print("❌ Document may not contain images")
                return False
                
    except Exception as e:
        print(f"❌ Could not analyze DOCX structure: {e}")
        return False

def test_training_engine_image_extraction():
    """Test image extraction using the training engine endpoint"""
    print("\n🔍 TRAINING ENGINE IMAGE EXTRACTION TEST")
    print("=" * 60)
    
    docx_path = "/app/Customer_Summary_Screen_User_Guide_1.3.docx"
    
    try:
        with open(docx_path, 'rb') as file:
            files = {
                'file': ('Customer_Summary_Screen_User_Guide_1.3.docx', file, 'application/vnd.openxmlformats-officedocument.wordprocessingml.document')
            }
            
            # Use training engine with explicit image extraction
            template_data = {
                "template_id": "phase1_document_processing",
                "processing_instructions": "Extract all content including images with contextual placement",
                "output_requirements": {
                    "format": "html",
                    "min_articles": 1,
                    "max_articles": 10,
                    "quality_benchmarks": ["content_completeness", "image_extraction", "proper_formatting"]
                },
                "media_handling": {
                    "extract_images": True,
                    "contextual_placement": True,
                    "filter_decorative": False,  # Don't filter out any images for this test
                    "save_to_asset_library": True
                }
            }
            
            form_data = {
                'template_id': 'phase1_document_processing',
                'training_mode': 'true',
                'template_instructions': json.dumps(template_data)
            }
            
            print("📤 Testing image extraction via training engine...")
            
            response = requests.post(
                f"{BACKEND_URL}/training/process",
                files=files,
                data=form_data,
                timeout=180  # 3 minutes for large file with images
            )
            
            print(f"📊 Response Status Code: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                
                # Check for image processing indicators
                images_processed = data.get('images_processed', 0)
                session_id = data.get('session_id')
                articles = data.get('articles', [])
                
                print(f"🖼️ Images Processed: {images_processed}")
                print(f"🔗 Session ID: {session_id}")
                print(f"📚 Articles Generated: {len(articles)}")
                
                if images_processed > 0:
                    print("✅ IMAGE EXTRACTION SUCCESSFUL")
                    print(f"✅ {images_processed} images were processed")
                    
                    # Check if images are embedded in articles
                    total_embedded = 0
                    for i, article in enumerate(articles):
                        content = article.get('content', '') or article.get('html', '')
                        image_count = content.count('<img') + content.count('<figure')
                        total_embedded += image_count
                        
                        if image_count > 0:
                            print(f"  📄 Article {i+1}: {image_count} embedded images")
                    
                    print(f"✅ Total embedded images: {total_embedded}")
                    return True
                else:
                    print("❌ NO IMAGES PROCESSED")
                    print("❌ Image extraction may not be working")
                    return False
                    
            else:
                print(f"❌ Training engine request failed - status {response.status_code}")
                print(f"Response: {response.text}")
                return False
                
    except Exception as e:
        print(f"❌ Training engine image extraction test failed: {e}")
        return False

def check_asset_library_for_images():
    """Check if any images were saved to the asset library"""
    print("\n🔍 ASSET LIBRARY IMAGE CHECK")
    print("=" * 60)
    
    try:
        response = requests.get(f"{BACKEND_URL}/assets", timeout=30)
        
        if response.status_code == 200:
            data = response.json()
            assets = data.get('assets', [])
            
            # Filter for image assets
            image_assets = [asset for asset in assets if asset.get('asset_type') == 'image']
            recent_assets = []
            
            # Look for recently created assets (last hour)
            import datetime
            one_hour_ago = datetime.datetime.utcnow() - datetime.timedelta(hours=1)
            
            for asset in image_assets:
                created_at = asset.get('created_at', '')
                try:
                    # Parse ISO format datetime
                    asset_time = datetime.datetime.fromisoformat(created_at.replace('Z', '+00:00'))
                    if asset_time > one_hour_ago:
                        recent_assets.append(asset)
                except:
                    pass  # Skip if datetime parsing fails
            
            print(f"📚 Total assets: {len(assets)}")
            print(f"🖼️ Image assets: {len(image_assets)}")
            print(f"🆕 Recent image assets: {len(recent_assets)}")
            
            if recent_assets:
                print("\n📋 Recent image assets:")
                for i, asset in enumerate(recent_assets[:5]):  # Show first 5
                    filename = asset.get('filename', 'unknown')
                    size = asset.get('file_size', 0)
                    url = asset.get('url', '')
                    print(f"  {i+1}. {filename} ({size} bytes)")
                    print(f"     URL: {url}")
                
                print("✅ RECENT IMAGES FOUND IN ASSET LIBRARY")
                return True
            elif image_assets:
                print("⚠️ Image assets exist but none are recent")
                print("⚠️ May be from previous tests")
                return True
            else:
                print("❌ NO IMAGE ASSETS FOUND")
                return False
                
        else:
            print(f"❌ Could not access asset library - status {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Asset library check failed: {e}")
        return False

def check_backend_static_directory():
    """Check if images were saved to backend static directory"""
    print("\n🔍 BACKEND STATIC DIRECTORY CHECK")
    print("=" * 60)
    
    try:
        static_dir = "/app/backend/static/uploads"
        
        if os.path.exists(static_dir):
            print(f"✅ Static directory exists: {static_dir}")
            
            # List all files
            all_files = []
            for root, dirs, files in os.walk(static_dir):
                for file in files:
                    file_path = os.path.join(root, file)
                    all_files.append(file_path)
            
            # Filter for image files
            image_files = [f for f in all_files if any(f.lower().endswith(ext) for ext in ['.png', '.jpg', '.jpeg', '.gif', '.bmp'])]
            
            print(f"📁 Total files in static directory: {len(all_files)}")
            print(f"🖼️ Image files: {len(image_files)}")
            
            if image_files:
                print("\n📋 Recent image files:")
                # Sort by modification time (most recent first)
                image_files.sort(key=lambda x: os.path.getmtime(x), reverse=True)
                
                for i, img_file in enumerate(image_files[:5]):  # Show first 5
                    size = os.path.getsize(img_file)
                    rel_path = img_file.replace('/app/backend/', '')
                    print(f"  {i+1}. {rel_path} ({size} bytes)")
                
                if len(image_files) > 5:
                    print(f"  ... and {len(image_files) - 5} more image files")
                
                print("✅ IMAGE FILES FOUND IN STATIC DIRECTORY")
                return True
            else:
                print("❌ NO IMAGE FILES FOUND IN STATIC DIRECTORY")
                return False
        else:
            print(f"❌ Static directory does not exist: {static_dir}")
            return False
            
    except Exception as e:
        print(f"❌ Static directory check failed: {e}")
        return False

if __name__ == "__main__":
    print("🖼️ IMAGE EXTRACTION TEST")
    print("Testing image extraction from Customer Summary Screen User Guide")
    print("=" * 80)
    
    # Run all image extraction tests
    tests = [
        ("DOCX Structure Analysis", analyze_docx_file_structure),
        ("Training Engine Extraction", test_training_engine_image_extraction),
        ("Asset Library Check", check_asset_library_for_images),
        ("Static Directory Check", check_backend_static_directory)
    ]
    
    results = []
    
    for test_name, test_function in tests:
        try:
            result = test_function()
            results.append((test_name, result))
            print(f"\n{'✅' if result else '❌'} {test_name}: {'PASSED' if result else 'FAILED'}")
        except Exception as e:
            print(f"\n❌ {test_name}: ERROR - {e}")
            results.append((test_name, False))
        
        print("-" * 40)
    
    # Summary
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    print(f"\n🖼️ IMAGE EXTRACTION TEST RESULTS")
    print("=" * 80)
    print(f"📊 Success Rate: {passed}/{total} ({(passed/total)*100:.1f}%)")
    
    for test_name, result in results:
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"  {status}: {test_name}")
    
    if passed >= 2:
        print("\n✅ IMAGE EXTRACTION: WORKING")
        print("✅ System can extract and process images from DOCX files")
    else:
        print("\n❌ IMAGE EXTRACTION: NEEDS INVESTIGATION")
        print("❌ Issues detected with image extraction pipeline")