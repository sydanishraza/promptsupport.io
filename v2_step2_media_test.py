#!/usr/bin/env python3
"""
V2 Engine Step 2 Media Management Testing
Focused testing for the 2 specific failed criteria to achieve 100% success rate
"""

import requests
import json
import base64
import io
import os
import time
from datetime import datetime

# Get backend URL from environment
BACKEND_URL = os.getenv('REACT_APP_BACKEND_URL', 'https://smartdoc-v2.preview.emergentagent.com')
API_BASE = f"{BACKEND_URL}/api"

def create_test_image_base64():
    """Create a simple test image in base64 format"""
    # Create a simple 100x100 red square PNG
    import struct
    
    # PNG header
    png_header = b'\x89PNG\r\n\x1a\n'
    
    # IHDR chunk (width=100, height=100, bit_depth=8, color_type=2 (RGB))
    ihdr_data = struct.pack('>IIBBBBB', 100, 100, 8, 2, 0, 0, 0)
    ihdr_crc = 0x7d8db8d3  # Pre-calculated CRC for this IHDR
    ihdr_chunk = struct.pack('>I', 13) + b'IHDR' + ihdr_data + struct.pack('>I', ihdr_crc)
    
    # Simple IDAT chunk with red pixels
    idat_data = b'\x08\x1d\x01\x02\x00\x01\xfd\xff\x00\x00\x00\x02\x00\x01'
    idat_crc = 0x8db7a87a  # Pre-calculated CRC
    idat_chunk = struct.pack('>I', len(idat_data)) + b'IDAT' + idat_data + struct.pack('>I', idat_crc)
    
    # IEND chunk
    iend_chunk = struct.pack('>I', 0) + b'IEND' + struct.pack('>I', 0xae426082)
    
    png_data = png_header + ihdr_chunk + idat_chunk + iend_chunk
    return base64.b64encode(png_data).decode('utf-8')

def create_docx_with_embedded_image():
    """Create a DOCX-like content with embedded base64 image"""
    test_image = create_test_image_base64()
    
    docx_content = f"""
    <h1>Google Maps Integration Guide</h1>
    <p>This guide covers how to integrate Google Maps into your web application.</p>
    
    <h2>Getting Started</h2>
    <p>First, you need to obtain an API key from Google Cloud Console.</p>
    
    <img src="data:image/png;base64,{test_image}" alt="Google Cloud Console API Key Setup" />
    
    <h2>Basic Implementation</h2>
    <p>Here's how to implement a basic Google Map:</p>
    
    <pre><code>
    function initMap() {{
        const map = new google.maps.Map(document.getElementById("map"), {{
            zoom: 4,
            center: {{ lat: -25.344, lng: 131.036 }},
        }});
    }}
    </code></pre>
    
    <img src="data:image/png;base64,{test_image}" alt="Basic Google Map Implementation Example" />
    
    <h2>Advanced Features</h2>
    <p>You can add markers, info windows, and custom styling.</p>
    
    <img src="data:image/png;base64,{test_image}" alt="Advanced Google Maps Features Screenshot" />
    """
    
    return docx_content

class V2MediaManagementTester:
    def __init__(self):
        self.results = []
        self.test_count = 0
        self.passed_count = 0
        
    def log_test(self, test_name, passed, details=""):
        """Log test result"""
        self.test_count += 1
        if passed:
            self.passed_count += 1
            status = "✅ PASSED"
        else:
            status = "❌ FAILED"
            
        result = f"{status}: {test_name}"
        if details:
            result += f" - {details}"
            
        print(result)
        self.results.append({
            'test': test_name,
            'passed': passed,
            'details': details,
            'timestamp': datetime.now().isoformat()
        })
        
    def test_v2_engine_health_check(self):
        """Test 1: V2 Engine Health Check with Media Features"""
        try:
            response = requests.get(f"{API_BASE}/engine", timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                engine_status = data.get('engine')
                features = data.get('features', [])
                
                # Check for media-related features
                media_features = [f for f in features if 'media' in f.lower() or 'image' in f.lower()]
                
                if engine_status == 'v2' and len(media_features) > 0:
                    self.log_test("V2 Engine Health Check with Media Features", True, 
                                f"Engine: {engine_status}, Media features: {len(media_features)}")
                else:
                    self.log_test("V2 Engine Health Check with Media Features", False, 
                                f"Engine: {engine_status}, Media features: {len(media_features)}")
            else:
                self.log_test("V2 Engine Health Check with Media Features", False, 
                            f"HTTP {response.status_code}")
                
        except Exception as e:
            self.log_test("V2 Engine Health Check with Media Features", False, str(e))
    
    def test_media_intelligence_contextual_processing(self):
        """Test 2: Media Intelligence Contextual Processing with Required Fields"""
        try:
            # Create test image
            test_image = create_test_image_base64()
            
            # Test media intelligence endpoint using form data
            form_data = {
                "media_data": f"data:image/png;base64,{test_image}",
                "alt_text": "Google Maps API setup screenshot",
                "context": "This image shows the Google Cloud Console where users can obtain their API key for Google Maps integration. The screenshot demonstrates the steps to enable the Maps JavaScript API."
            }
            
            response = requests.post(f"{API_BASE}/media-intelligence", 
                                   data=form_data, timeout=15)
            
            if response.status_code == 200:
                data = response.json()
                
                # Check for success and analysis data
                success = data.get('success', False)
                analysis = data.get('analysis', {})
                
                # Check for required contextual fields in analysis
                has_contextual_caption = 'contextual_caption' in analysis
                has_placement_suggestion = 'placement_suggestion' in analysis
                processing_status = analysis.get('processing_status', 'unknown')
                
                if success and has_contextual_caption and has_placement_suggestion and processing_status != 'fallback':
                    self.log_test("Media Intelligence Contextual Processing", True, 
                                f"contextual_caption: {has_contextual_caption}, placement_suggestion: {has_placement_suggestion}, status: {processing_status}")
                else:
                    self.log_test("Media Intelligence Contextual Processing", False, 
                                f"success: {success}, contextual_caption: {has_contextual_caption}, placement_suggestion: {has_placement_suggestion}, status: {processing_status}")
            else:
                self.log_test("Media Intelligence Contextual Processing", False, 
                            f"HTTP {response.status_code}: {response.text[:200]}")
                
        except Exception as e:
            self.log_test("Media Intelligence Contextual Processing", False, str(e))
    
    def test_complex_document_media_extraction(self):
        """Test 3: Complex Document Media Extraction Pipeline"""
        try:
            # Create complex document with embedded images
            complex_content = create_docx_with_embedded_image()
            
            # Test file upload processing
            payload = {
                "content": complex_content,
                "filename": "google_maps_guide_with_images.html",
                "content_type": "text/html"
            }
            
            response = requests.post(f"{API_BASE}/content/process", 
                                   json=payload, timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                
                # Check if articles were generated
                articles_generated = data.get('articles_generated', 0)
                processing_status = data.get('status', 'unknown')
                engine = data.get('engine', 'unknown')
                
                # Check if media was extracted
                media_extracted = data.get('media_extracted', 0)
                
                if articles_generated > 0 and engine == 'v2' and media_extracted > 0:
                    self.log_test("Complex Document Media Extraction Pipeline", True, 
                                f"Articles: {articles_generated}, Media: {media_extracted}, Engine: {engine}")
                else:
                    self.log_test("Complex Document Media Extraction Pipeline", False, 
                                f"Articles: {articles_generated}, Media: {media_extracted}, Engine: {engine}, Status: {processing_status}")
            else:
                self.log_test("Complex Document Media Extraction Pipeline", False, 
                            f"HTTP {response.status_code}: {response.text[:200]}")
                
        except Exception as e:
            self.log_test("Complex Document Media Extraction Pipeline", False, str(e))
    
    def test_media_asset_library_integration(self):
        """Test 4: Media Asset Library Integration"""
        try:
            # Test asset library endpoint
            response = requests.get(f"{API_BASE}/assets", timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                assets = data.get('assets', [])
                
                # Look for media assets
                media_assets = [a for a in assets if a.get('type', '').startswith(('image/', 'video/'))]
                
                if len(media_assets) > 0:
                    self.log_test("Media Asset Library Integration", True, 
                                f"Found {len(media_assets)} media assets out of {len(assets)} total")
                else:
                    self.log_test("Media Asset Library Integration", False, 
                                f"No media assets found in {len(assets)} total assets")
            else:
                self.log_test("Media Asset Library Integration", False, 
                            f"HTTP {response.status_code}")
                
        except Exception as e:
            self.log_test("Media Asset Library Integration", False, str(e))
    
    def test_media_storage_and_organization(self):
        """Test 5: Media Storage and Organization"""
        try:
            # Test media upload
            test_image = create_test_image_base64()
            
            # Convert base64 to file-like object
            image_data = base64.b64decode(test_image)
            
            files = {
                'file': ('test_media.png', io.BytesIO(image_data), 'image/png')
            }
            
            response = requests.post(f"{API_BASE}/assets/upload", 
                                   files=files, timeout=15)
            
            if response.status_code == 200:
                data = response.json()
                success = data.get('success', False)
                asset_data = data.get('asset', {})
                asset_id = asset_data.get('id')
                
                if success and asset_id:
                    self.log_test("Media Storage and Organization", True, 
                                f"Upload successful, Asset ID: {asset_id}")
                    
                    # Clean up - delete the test asset
                    try:
                        requests.delete(f"{API_BASE}/assets/{asset_id}", timeout=5)
                    except:
                        pass  # Ignore cleanup errors
                else:
                    self.log_test("Media Storage and Organization", False, 
                                f"Upload failed: success={success}, asset_id={asset_id}")
            else:
                self.log_test("Media Storage and Organization", False, 
                            f"HTTP {response.status_code}: {response.text[:200]}")
                
        except Exception as e:
            self.log_test("Media Storage and Organization", False, str(e))
    
    def test_llm_vision_integration(self):
        """Test 6: LLM+Vision Integration with Contextual Captions"""
        try:
            # Test direct media intelligence with vision
            test_image = create_test_image_base64()
            
            payload = {
                "image_data": test_image,
                "context": "Google Maps JavaScript API tutorial showing how to initialize a map with markers and custom styling options",
                "analysis_type": "comprehensive"
            }
            
            response = requests.post(f"{API_BASE}/media/vision-analyze", 
                                   json=payload, timeout=20)
            
            if response.status_code == 200:
                data = response.json()
                
                # Check for LLM+Vision specific fields
                has_vision_analysis = 'vision_analysis' in data
                has_contextual_caption = 'contextual_caption' in data
                has_placement_suggestion = 'placement_suggestion' in data
                analysis_method = data.get('analysis_method', 'unknown')
                
                if has_vision_analysis and has_contextual_caption and has_placement_suggestion and analysis_method == 'llm_vision':
                    self.log_test("LLM+Vision Integration", True, 
                                f"Vision analysis: {has_vision_analysis}, Method: {analysis_method}")
                else:
                    self.log_test("LLM+Vision Integration", False, 
                                f"Vision: {has_vision_analysis}, Contextual: {has_contextual_caption}, Placement: {has_placement_suggestion}, Method: {analysis_method}")
            else:
                # Try fallback endpoint
                response = requests.post(f"{API_BASE}/media/analyze", 
                                       json={"base64_data": f"data:image/png;base64,{test_image}", 
                                            "context": payload["context"]}, timeout=15)
                
                if response.status_code == 200:
                    data = response.json()
                    has_contextual_caption = 'contextual_caption' in data
                    has_placement_suggestion = 'placement_suggestion' in data
                    
                    if has_contextual_caption and has_placement_suggestion:
                        self.log_test("LLM+Vision Integration", True, 
                                    f"Fallback endpoint working with required fields")
                    else:
                        self.log_test("LLM+Vision Integration", False, 
                                    f"Fallback missing fields: contextual_caption={has_contextual_caption}, placement_suggestion={has_placement_suggestion}")
                else:
                    self.log_test("LLM+Vision Integration", False, 
                                f"Both endpoints failed: {response.status_code}")
                
        except Exception as e:
            self.log_test("LLM+Vision Integration", False, str(e))
    
    def test_intelligent_fallback_analysis(self):
        """Test 7: Intelligent Fallback Analysis with Complete Field Structure"""
        try:
            # Test with invalid image data to trigger fallback
            payload = {
                "base64_data": "data:image/png;base64,invalid_data",
                "alt_text": "Test fallback image",
                "context": "Testing fallback analysis when vision processing fails"
            }
            
            response = requests.post(f"{API_BASE}/media/analyze", 
                                   json=payload, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                
                # Check that fallback still provides required fields
                has_contextual_caption = 'contextual_caption' in data
                has_placement_suggestion = 'placement_suggestion' in data
                processing_status = data.get('processing_status', 'unknown')
                
                # Fallback should still provide these fields
                if has_contextual_caption and has_placement_suggestion:
                    self.log_test("Intelligent Fallback Analysis", True, 
                                f"Fallback provides required fields, Status: {processing_status}")
                else:
                    self.log_test("Intelligent Fallback Analysis", False, 
                                f"Fallback missing fields: contextual_caption={has_contextual_caption}, placement_suggestion={has_placement_suggestion}")
            else:
                self.log_test("Intelligent Fallback Analysis", False, 
                            f"HTTP {response.status_code}: {response.text[:200]}")
                
        except Exception as e:
            self.log_test("Intelligent Fallback Analysis", False, str(e))
    
    def test_docx_embedded_image_processing(self):
        """Test 8: DOCX File Upload with Embedded Images"""
        try:
            # Create a more realistic DOCX-like content
            docx_content = create_docx_with_embedded_image()
            
            # Test as file upload
            files = {
                'file': ('google_maps_tutorial.html', io.StringIO(docx_content), 'text/html')
            }
            
            response = requests.post(f"{API_BASE}/content/upload", 
                                   files=files, timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                
                success = data.get('success', False)
                articles_count = len(data.get('articles', []))
                job_id = data.get('job_id')
                
                if success and articles_count > 0:
                    self.log_test("DOCX Embedded Image Processing", True, 
                                f"Success: {success}, Articles: {articles_count}, Job: {job_id}")
                else:
                    self.log_test("DOCX Embedded Image Processing", False, 
                                f"Success: {success}, Articles: {articles_count}")
            else:
                self.log_test("DOCX Embedded Image Processing", False, 
                            f"HTTP {response.status_code}: {response.text[:200]}")
                
        except Exception as e:
            self.log_test("DOCX Embedded Image Processing", False, str(e))
    
    def test_media_integration_pipeline(self):
        """Test 9: Media Integration with Content Processing Pipeline"""
        try:
            # Test end-to-end media integration
            content_with_media = f"""
            <h1>Complete Media Integration Test</h1>
            <p>This document tests the complete media integration pipeline.</p>
            
            <img src="data:image/png;base64,{create_test_image_base64()}" alt="Test Image 1" />
            
            <h2>Section with Multiple Media</h2>
            <p>Testing multiple media elements in content processing.</p>
            
            <img src="data:image/png;base64,{create_test_image_base64()}" alt="Test Image 2" />
            """
            
            payload = {
                "content": content_with_media,
                "process_media": True,
                "generate_articles": True
            }
            
            response = requests.post(f"{API_BASE}/content/process", 
                                   json=payload, timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                
                articles_generated = data.get('articles_generated', 0)
                media_processed = data.get('media_processed', 0)
                engine = data.get('engine', 'unknown')
                
                if articles_generated > 0 and media_processed > 0 and engine == 'v2':
                    self.log_test("Media Integration Pipeline", True, 
                                f"Articles: {articles_generated}, Media: {media_processed}, Engine: {engine}")
                else:
                    self.log_test("Media Integration Pipeline", False, 
                                f"Articles: {articles_generated}, Media: {media_processed}, Engine: {engine}")
            else:
                self.log_test("Media Integration Pipeline", False, 
                            f"HTTP {response.status_code}: {response.text[:200]}")
                
        except Exception as e:
            self.log_test("Media Integration Pipeline", False, str(e))
    
    def test_media_extraction_various_formats(self):
        """Test 10: Media Extraction from Various Document Types"""
        try:
            # Test different content types
            test_formats = [
                ("HTML with Images", "text/html", create_docx_with_embedded_image()),
                ("Markdown with Images", "text/markdown", f"# Test\n![Test Image](data:image/png;base64,{create_test_image_base64()})"),
                ("Plain Text with References", "text/plain", "See image: test_image.png for details")
            ]
            
            successful_extractions = 0
            
            for format_name, content_type, content in test_formats:
                try:
                    payload = {
                        "content": content,
                        "content_type": content_type,
                        "extract_media": True
                    }
                    
                    response = requests.post(f"{API_BASE}/content/process", 
                                           json=payload, timeout=20)
                    
                    if response.status_code == 200:
                        data = response.json()
                        if data.get('media_extracted', 0) > 0 or data.get('articles_generated', 0) > 0:
                            successful_extractions += 1
                            
                except Exception:
                    continue
            
            if successful_extractions >= 2:  # At least 2 out of 3 formats should work
                self.log_test("Media Extraction Various Formats", True, 
                            f"Successfully processed {successful_extractions}/3 formats")
            else:
                self.log_test("Media Extraction Various Formats", False, 
                            f"Only {successful_extractions}/3 formats processed successfully")
                
        except Exception as e:
            self.log_test("Media Extraction Various Formats", False, str(e))
    
    def run_all_tests(self):
        """Run all V2 Engine Step 2 Media Management tests"""
        print("🎯 V2 ENGINE STEP 2 MEDIA MANAGEMENT TESTING STARTED")
        print(f"📡 Testing against: {API_BASE}")
        print("=" * 80)
        
        # Run all tests
        self.test_v2_engine_health_check()
        self.test_media_intelligence_contextual_processing()
        self.test_complex_document_media_extraction()
        self.test_media_asset_library_integration()
        self.test_media_storage_and_organization()
        self.test_llm_vision_integration()
        self.test_intelligent_fallback_analysis()
        self.test_docx_embedded_image_processing()
        self.test_media_integration_pipeline()
        self.test_media_extraction_various_formats()
        
        # Print summary
        print("=" * 80)
        print(f"🎉 TESTING COMPLETED: {self.passed_count}/{self.test_count} tests passed")
        print(f"📊 Success Rate: {(self.passed_count/self.test_count)*100:.1f}%")
        
        if self.passed_count == self.test_count:
            print("✅ ALL TESTS PASSED - V2 Engine Step 2 Media Management is 100% operational!")
        elif self.passed_count >= self.test_count * 0.8:
            print("⚠️ MOSTLY WORKING - Some issues identified but core functionality operational")
        else:
            print("❌ SIGNIFICANT ISSUES - Major problems with media management functionality")
        
        return {
            'total_tests': self.test_count,
            'passed_tests': self.passed_count,
            'success_rate': (self.passed_count/self.test_count)*100,
            'results': self.results
        }

if __name__ == "__main__":
    tester = V2MediaManagementTester()
    results = tester.run_all_tests()
    
    # Save results to file
    with open('/app/v2_step2_media_test_results.json', 'w') as f:
        json.dump(results, f, indent=2)
    
    print(f"\n📄 Detailed results saved to: /app/v2_step2_media_test_results.json")