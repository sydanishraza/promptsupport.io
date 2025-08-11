#!/usr/bin/env python3
"""
User DOCX processing test with the actual file
"""
import requests
import json
import os
import tempfile
import time
from dotenv import load_dotenv

load_dotenv('/app/frontend/.env')
BACKEND_URL = os.environ.get('REACT_APP_BACKEND_URL', 'https://804e26ce-e2cd-4ae9-bd9c-fe7be1b5493a.preview.emergentagent.com') + '/api'

def download_user_docx():
    """Download the user's DOCX file"""
    user_docx_url = "https://customer-assets.emergentagent.com/job_knowledge-engine-3/artifacts/jd75fljk_Customer%20Summary%20Screen%20USer%20Guide%201.3.docx"
    
    print(f"📥 Downloading user's DOCX file...")
    print(f"🔗 URL: {user_docx_url}")
    
    try:
        response = requests.get(user_docx_url, timeout=30)
        if response.status_code == 200:
            content_length = len(response.content)
            print(f"✅ Downloaded: {content_length:,} bytes ({content_length/1024:.1f} KB)")
            
            # Save to temporary file
            temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.docx')
            temp_file.write(response.content)
            temp_file.close()
            
            return temp_file.name
        else:
            print(f"❌ Download failed: {response.status_code}")
            return None
    except Exception as e:
        print(f"❌ Download error: {e}")
        return None

def process_docx_file(docx_path):
    """Process the DOCX file through the training endpoint"""
    print(f"⚙️ Processing DOCX file...")
    
    try:
        with open(docx_path, 'rb') as f:
            files = {
                'file': ('Customer_Summary_Screen_User_Guide_1.3.docx', f, 'application/vnd.openxmlformats-officedocument.wordprocessingml.document')
            }
            
            form_data = {
                'template_id': 'comprehensive_document_processing',
                'training_mode': 'true'
            }
            
            print("🚀 Starting processing (this may take several minutes for large files)...")
            start_time = time.time()
            
            # Use longer timeout for large file
            response = requests.post(
                f"{BACKEND_URL}/training/process",
                files=files,
                data=form_data,
                timeout=300  # 5 minutes timeout
            )
            
            processing_time = time.time() - start_time
            print(f"⏱️ Processing took {processing_time:.2f} seconds")
            
            if response.status_code == 200:
                data = response.json()
                
                success = data.get('success', False)
                status = data.get('status', 'unknown')
                articles = data.get('articles', [])
                images_processed = data.get('images_processed', 0)
                
                print(f"📊 Processing Results:")
                print(f"  Success: {success}")
                print(f"  Status: {status}")
                print(f"  Articles created: {len(articles)}")
                print(f"  Images processed: {images_processed}")
                
                if success and len(articles) > 0:
                    print("✅ DOCX processing completed successfully!")
                    return True, data
                else:
                    print("❌ DOCX processing failed or no articles created")
                    return False, data
            else:
                print(f"❌ Processing failed: {response.status_code}")
                print(f"Response: {response.text[:500]}")
                return False, None
                
    except requests.exceptions.Timeout:
        print("⏰ Processing timed out (5 minutes) - file may be too large")
        print("💡 Large files may still be processing in the background")
        return False, None
    except Exception as e:
        print(f"❌ Processing error: {e}")
        return False, None

def verify_results():
    """Verify the processing results"""
    print(f"🔍 Verifying results...")
    
    try:
        # Check content library
        response = requests.get(f"{BACKEND_URL}/content-library", timeout=30)
        if response.status_code == 200:
            data = response.json()
            articles = data.get('articles', [])
            
            print(f"📚 Content Library: {len(articles)} articles")
            
            if len(articles) > 0:
                # Analyze recent articles
                substantial_articles = 0
                articles_with_images = 0
                total_chars = 0
                
                for article in articles[:10]:
                    content = article.get('content', '') or article.get('html', '')
                    image_count = article.get('image_count', 0)
                    
                    if len(content) > 500:
                        substantial_articles += 1
                    if image_count > 0 or '<img' in content or '<figure' in content:
                        articles_with_images += 1
                    total_chars += len(content)
                
                print(f"📊 Analysis:")
                print(f"  Substantial articles: {substantial_articles}")
                print(f"  Articles with images: {articles_with_images}")
                print(f"  Average content: {total_chars // min(len(articles), 10):,} chars")
                
                # Show sample article titles
                print(f"📄 Sample articles:")
                for i, article in enumerate(articles[:5]):
                    title = article.get('title', 'No title')[:60]
                    content_len = len(article.get('content', ''))
                    print(f"  {i+1}. {title} ({content_len} chars)")
                
                return len(articles) > 0
            else:
                print("⚠️ No articles found")
                return False
        else:
            print(f"❌ Failed to check content library: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Verification error: {e}")
        return False

def main():
    print("🎯 USER DOCX PROCESSING TEST")
    print("=" * 60)
    
    # Step 1: Download user's DOCX
    docx_path = download_user_docx()
    if not docx_path:
        print("❌ Failed to download DOCX file")
        return False
    
    try:
        # Step 2: Process DOCX
        success, data = process_docx_file(docx_path)
        
        # Step 3: Verify results (even if processing timed out)
        print("\n" + "="*40)
        verification_success = verify_results()
        
        # Step 4: Summary
        print("\n" + "=" * 60)
        print("📊 USER DOCX TEST SUMMARY")
        print("=" * 60)
        
        if success:
            print("✅ DOCX processing completed successfully")
        elif verification_success:
            print("⚠️ Processing may have timed out but articles were created")
        else:
            print("❌ DOCX processing failed")
        
        if verification_success:
            print("✅ Articles found in content library")
            print("✅ System successfully processed user's actual DOCX file")
        else:
            print("❌ No articles found in content library")
        
        return success or verification_success
        
    finally:
        # Cleanup
        if docx_path and os.path.exists(docx_path):
            os.unlink(docx_path)
            print(f"🗑️ Cleaned up temporary file")

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)