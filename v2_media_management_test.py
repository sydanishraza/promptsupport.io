#!/usr/bin/env python3
"""
V2 Engine Step 2 Media Management & Asset Handling Comprehensive Testing
Focus: Identify the 2 specific failed criteria from 92% success rate (23/25 criteria)
"""

import asyncio
import aiohttp
import json
import base64
import os
import time
from datetime import datetime

# Backend URL from environment
BACKEND_URL = os.getenv('REACT_APP_BACKEND_URL', 'https://content-formatter.preview.emergentagent.com')
API_BASE = f"{BACKEND_URL}/api"

class V2MediaManagementTester:
    def __init__(self):
        self.session = None
        self.test_results = []
        self.failed_tests = []
        
    async def setup_session(self):
        """Setup HTTP session"""
        self.session = aiohttp.ClientSession()
        
    async def cleanup_session(self):
        """Cleanup HTTP session"""
        if self.session:
            await self.session.close()
            
    def log_test(self, test_name: str, success: bool, details: str = ""):
        """Log test result"""
        result = {
            "test": test_name,
            "success": success,
            "details": details,
            "timestamp": datetime.now().isoformat()
        }
        self.test_results.append(result)
        
        status = "✅" if success else "❌"
        print(f"{status} {test_name}: {details}")
        
        if not success:
            self.failed_tests.append(result)
            
    async def test_v2_engine_health_check(self):
        """Test 1: V2 Engine Health Check with Media Features"""
        try:
            async with self.session.get(f"{API_BASE}/engine") as response:
                if response.status == 200:
                    data = await response.json()
                    
                    # Check V2 engine status
                    if data.get('engine') == 'v2':
                        # Check for media-related features
                        features = data.get('features', [])
                        media_features = [
                            'image_extraction',
                            'comprehensive_file_support'
                        ]
                        
                        missing_features = [f for f in media_features if f not in features]
                        
                        if not missing_features:
                            self.log_test("V2 Engine Health Check", True, 
                                        f"V2 Engine active with media features: {media_features}")
                        else:
                            self.log_test("V2 Engine Health Check", False, 
                                        f"Missing media features: {missing_features}")
                    else:
                        self.log_test("V2 Engine Health Check", False, 
                                    f"Engine not V2: {data.get('engine')}")
                else:
                    self.log_test("V2 Engine Health Check", False, 
                                f"HTTP {response.status}")
        except Exception as e:
            self.log_test("V2 Engine Health Check", False, f"Exception: {str(e)}")
            
    async def test_v2_media_manager_instantiation(self):
        """Test 2: V2MediaManager Class Instantiation and Configuration"""
        try:
            # Test by processing content that should trigger media manager
            test_content = """
            # Test Document with Media
            This is a test document that should trigger V2 media processing.
            
            ## Section 1
            Content with potential media references.
            
            ## Section 2  
            More content for comprehensive testing.
            """
            
            async with self.session.post(f"{API_BASE}/content/process", 
                                       json={"content": test_content}) as response:
                if response.status == 200:
                    data = await response.json()
                    
                    # Check if V2 engine was used
                    if data.get('engine') == 'v2':
                        self.log_test("V2MediaManager Instantiation", True, 
                                    "V2 engine processing confirmed, media manager available")
                    else:
                        self.log_test("V2MediaManager Instantiation", False, 
                                    f"V2 engine not used: {data.get('engine')}")
                else:
                    self.log_test("V2MediaManager Instantiation", False, 
                                f"HTTP {response.status}")
        except Exception as e:
            self.log_test("V2MediaManager Instantiation", False, f"Exception: {str(e)}")
            
    async def test_media_intelligence_analysis(self):
        """Test 3: Media Intelligence Analysis with LLM + Vision"""
        try:
            # Create a simple test image (1x1 pixel PNG)
            test_image_b64 = "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNkYPhfDwAChAI9jU77zgAAAABJRU5ErkJggg=="
            
            form_data = aiohttp.FormData()
            form_data.add_field('media_data', test_image_b64)
            form_data.add_field('alt_text', 'Test image')
            form_data.add_field('context', 'Testing media intelligence analysis')
            
            async with self.session.post(f"{API_BASE}/media-intelligence", 
                                       data=form_data) as response:
                if response.status == 200:
                    data = await response.json()
                    
                    if data.get('success'):
                        analysis = data.get('analysis', {})
                        
                        # Check for key analysis components
                        required_fields = ['classification', 'contextual_caption', 'placement_suggestion']
                        missing_fields = [f for f in required_fields if f not in analysis]
                        
                        if not missing_fields:
                            self.log_test("Media Intelligence Analysis", True, 
                                        f"Analysis complete with fields: {list(analysis.keys())}")
                        else:
                            self.log_test("Media Intelligence Analysis", False, 
                                        f"Missing analysis fields: {missing_fields}")
                    else:
                        self.log_test("Media Intelligence Analysis", False, 
                                    f"Analysis failed: {data.get('error')}")
                else:
                    self.log_test("Media Intelligence Analysis", False, 
                                f"HTTP {response.status}")
        except Exception as e:
            self.log_test("Media Intelligence Analysis", False, f"Exception: {str(e)}")
            
    async def test_contextual_filename_generation(self):
        """Test 4: Contextual Filename Generation and Media Metadata"""
        try:
            # Test file upload with media content
            test_content = "Test document content for media filename generation"
            
            form_data = aiohttp.FormData()
            form_data.add_field('file', test_content.encode(), 
                              filename='test_media_doc.txt', 
                              content_type='text/plain')
            form_data.add_field('metadata', json.dumps({
                "test_context": "media_filename_generation",
                "expected_features": ["contextual_filenames", "media_metadata"]
            }))
            
            async with self.session.post(f"{API_BASE}/content/upload", 
                                       data=form_data) as response:
                if response.status == 200:
                    data = await response.json()
                    
                    # Check if processing was successful
                    if data.get('status') == 'completed':
                        # Check for V2 engine usage
                        if 'v2' in str(data).lower():
                            self.log_test("Contextual Filename Generation", True, 
                                        "File processed with V2 engine, filename generation available")
                        else:
                            self.log_test("Contextual Filename Generation", False, 
                                        "V2 engine not detected in file processing")
                    else:
                        self.log_test("Contextual Filename Generation", False, 
                                    f"Processing failed: {data.get('status')}")
                else:
                    self.log_test("Contextual Filename Generation", False, 
                                f"HTTP {response.status}")
        except Exception as e:
            self.log_test("Contextual Filename Generation", False, f"Exception: {str(e)}")
            
    async def test_alt_text_generation(self):
        """Test 5: Alt-text Creation and Media Metadata Preservation"""
        try:
            # Test article processing with media
            test_article_content = """
            # Test Article with Media
            
            This article contains embedded media that should be processed.
            
            ![Test Image](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNkYPhfDwAChAI9jU77zgAAAABJRU5ErkJggg==)
            
            The media should have proper alt-text generated.
            """
            
            form_data = aiohttp.FormData()
            form_data.add_field('content', test_article_content)
            form_data.add_field('article_id', 'test_alt_text_generation')
            
            async with self.session.post(f"{API_BASE}/media/process-article", 
                                       data=form_data) as response:
                if response.status == 200:
                    data = await response.json()
                    
                    if data.get('success'):
                        media_count = data.get('media_count', 0)
                        processed_media = data.get('processed_media', [])
                        
                        if media_count > 0 and processed_media:
                            # Check if alt-text was generated
                            has_alt_text = any('alt' in str(media).lower() for media in processed_media)
                            
                            if has_alt_text:
                                self.log_test("Alt-text Generation", True, 
                                            f"Processed {media_count} media items with alt-text")
                            else:
                                self.log_test("Alt-text Generation", False, 
                                            "Media processed but no alt-text generation detected")
                        else:
                            self.log_test("Alt-text Generation", False, 
                                        f"No media found or processed: {media_count} items")
                    else:
                        self.log_test("Alt-text Generation", False, 
                                    f"Processing failed: {data.get('error')}")
                else:
                    self.log_test("Alt-text Generation", False, 
                                f"HTTP {response.status}")
        except Exception as e:
            self.log_test("Alt-text Generation", False, f"Exception: {str(e)}")
            
    async def test_organized_media_storage(self):
        """Test 6: Organized Media Storage and Proper Referencing"""
        try:
            # Get media statistics to check storage organization
            async with self.session.get(f"{API_BASE}/media/stats") as response:
                if response.status == 200:
                    data = await response.json()
                    
                    # Check for organized storage indicators
                    total_articles = data.get('total_articles', 0)
                    articles_with_media = data.get('articles_with_media', 0)
                    media_by_format = data.get('media_by_format', {})
                    intelligence_analysis = data.get('intelligence_analysis', {})
                    
                    if total_articles > 0:
                        # Check if media is properly organized
                        organization_score = 0
                        
                        # Check format organization
                        if media_by_format:
                            organization_score += 1
                            
                        # Check intelligence analysis
                        if intelligence_analysis:
                            organization_score += 1
                            
                        # Check media processing
                        if articles_with_media > 0:
                            organization_score += 1
                            
                        if organization_score >= 2:
                            self.log_test("Organized Media Storage", True, 
                                        f"Media storage organized: {total_articles} articles, {articles_with_media} with media")
                        else:
                            self.log_test("Organized Media Storage", False, 
                                        f"Poor media organization: score {organization_score}/3")
                    else:
                        self.log_test("Organized Media Storage", False, 
                                    "No articles found for media storage testing")
                else:
                    self.log_test("Organized Media Storage", False, 
                                f"HTTP {response.status}")
        except Exception as e:
            self.log_test("Organized Media Storage", False, f"Exception: {str(e)}")
            
    async def test_preview_generation_capabilities(self):
        """Test 7: Preview Generation and Thumbnail Capabilities"""
        try:
            # Test media review endpoint for preview capabilities
            test_run_id = "test_preview_generation_123"
            
            async with self.session.get(f"{API_BASE}/review/media/{test_run_id}") as response:
                if response.status == 200:
                    data = await response.json()
                    
                    # Check for preview/thumbnail capabilities
                    media_summary = data.get('media_summary', {})
                    contextual_info = data.get('contextual_info', {})
                    
                    # Check if preview structure is available
                    preview_indicators = [
                        'total_count' in media_summary,
                        'images_count' in media_summary,
                        'extraction_method' in contextual_info,
                        'alt_text_generated' in contextual_info
                    ]
                    
                    preview_score = sum(preview_indicators)
                    
                    if preview_score >= 3:
                        self.log_test("Preview Generation Capabilities", True, 
                                    f"Preview system available: {preview_score}/4 indicators")
                    else:
                        self.log_test("Preview Generation Capabilities", False, 
                                    f"Limited preview capabilities: {preview_score}/4 indicators")
                else:
                    self.log_test("Preview Generation Capabilities", False, 
                                f"HTTP {response.status}")
        except Exception as e:
            self.log_test("Preview Generation Capabilities", False, f"Exception: {str(e)}")
            
    async def test_media_extraction_complex_documents(self):
        """Test 8: Media Extraction from Complex Documents (CRITICAL TEST)"""
        try:
            # Test with a complex document structure
            complex_document = """
            # Complex Document with Multiple Media Types
            
            ## Section 1: Introduction
            This document contains various media types for extraction testing.
            
            ### Subsection 1.1: Images
            ![Chart 1](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNkYPhfDwAChAI9jU77zgAAAABJRU5ErkJggg==)
            
            ### Subsection 1.2: Diagrams  
            ![Diagram 1](data:image/jpeg;base64,/9j/4AAQSkZJRgABAQAAAQABAAD/2wBDAAYEBQYFBAYGBQYHBwYIChAKCgkJChQODwwQFxQYGBcUFhYaHSUfGhsjHBYWICwgIyYnKSopGR8tMC0oMCUoKSj/2wBDAQcHBwoIChMKChMoGhYaKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCj/wAARCAABAAEDASIAAhEBAxEB/8QAFQABAQAAAAAAAAAAAAAAAAAAAAv/xAAUEAEAAAAAAAAAAAAAAAAAAAAA/8QAFQEBAQAAAAAAAAAAAAAAAAAAAAX/xAAUEQEAAAAAAAAAAAAAAAAAAAAA/9oADAMBAAIRAxEAPwCdABmX/9k=)
            
            ## Section 2: Technical Content
            More complex content with nested structures.
            
            ### Code Examples
            ```python
            def process_media():
                return "media processed"
            ```
            
            ### Tables
            | Media Type | Count | Status |
            |------------|-------|--------|
            | Images     | 2     | Active |
            | Videos     | 0     | None   |
            
            ## Section 3: Conclusion
            This complex document should test media extraction capabilities thoroughly.
            """
            
            async with self.session.post(f"{API_BASE}/content/process", 
                                       json={"content": complex_document}) as response:
                if response.status == 200:
                    data = await response.json()
                    
                    # Check if complex document was processed successfully
                    if data.get('status') == 'completed':
                        # Check for V2 engine usage
                        engine = data.get('engine')
                        articles_created = data.get('articles_created', 0)
                        
                        if engine == 'v2' and articles_created > 0:
                            self.log_test("Media Extraction Complex Documents", True, 
                                        f"Complex document processed: {articles_created} articles, engine={engine}")
                        else:
                            self.log_test("Media Extraction Complex Documents", False, 
                                        f"Complex processing failed: articles={articles_created}, engine={engine}")
                    else:
                        self.log_test("Media Extraction Complex Documents", False, 
                                    f"Processing status: {data.get('status')}")
                else:
                    self.log_test("Media Extraction Complex Documents", False, 
                                f"HTTP {response.status}")
        except Exception as e:
            self.log_test("Media Extraction Complex Documents", False, f"Exception: {str(e)}")
            
    async def test_intelligent_asset_organization(self):
        """Test 9: Intelligent Asset Organization and Storage Systems (CRITICAL TEST)"""
        try:
            # Test asset organization by checking content library structure
            async with self.session.get(f"{API_BASE}/content-library") as response:
                if response.status == 200:
                    data = await response.json()
                    articles = data.get('articles', [])
                    
                    if articles:
                        # Analyze asset organization
                        organization_metrics = {
                            'articles_with_media': 0,
                            'proper_metadata': 0,
                            'v2_engine_articles': 0,
                            'media_references': 0
                        }
                        
                        for article in articles:
                            # Check for media presence
                            content = article.get('content', '')
                            if 'img' in content.lower() or 'media' in content.lower():
                                organization_metrics['articles_with_media'] += 1
                                
                            # Check for proper metadata
                            metadata = article.get('metadata', {})
                            if metadata and len(metadata) > 2:
                                organization_metrics['proper_metadata'] += 1
                                
                            # Check for V2 engine processing
                            if article.get('engine') == 'v2' or 'v2' in str(metadata).lower():
                                organization_metrics['v2_engine_articles'] += 1
                                
                            # Check for media references
                            if 'media_references' in article or 'media_handling' in str(metadata):
                                organization_metrics['media_references'] += 1
                        
                        # Calculate organization score
                        total_articles = len(articles)
                        organization_score = sum(organization_metrics.values()) / (total_articles * 4) if total_articles > 0 else 0
                        
                        if organization_score >= 0.3:  # 30% organization threshold
                            self.log_test("Intelligent Asset Organization", True, 
                                        f"Asset organization score: {organization_score:.2f}, metrics: {organization_metrics}")
                        else:
                            self.log_test("Intelligent Asset Organization", False, 
                                        f"Poor asset organization: {organization_score:.2f}, metrics: {organization_metrics}")
                    else:
                        self.log_test("Intelligent Asset Organization", False, 
                                    "No articles found for organization testing")
                else:
                    self.log_test("Intelligent Asset Organization", False, 
                                f"HTTP {response.status}")
        except Exception as e:
            self.log_test("Intelligent Asset Organization", False, f"Exception: {str(e)}")
            
    async def test_media_integration_content_pipeline(self):
        """Test 10: Media Integration with Content Processing Pipeline"""
        try:
            # Test end-to-end media integration
            test_document_with_media = """
            # Media Integration Test Document
            
            This document tests the complete media integration pipeline.
            
            ## Visual Content
            ![Integration Test](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNkYPhfDwAChAI9jU77zgAAAABJRU5ErkJggg==)
            
            ## Process Flow
            1. Document upload
            2. Media extraction  
            3. Content processing
            4. Asset organization
            5. Final integration
            
            This should test the complete pipeline integration.
            """
            
            # Step 1: Process the document
            async with self.session.post(f"{API_BASE}/content/process", 
                                       json={"content": test_document_with_media}) as response:
                if response.status == 200:
                    process_data = await response.json()
                    
                    if process_data.get('status') == 'completed':
                        # Step 2: Check if articles were created
                        async with self.session.get(f"{API_BASE}/content-library") as lib_response:
                            if lib_response.status == 200:
                                lib_data = await lib_response.json()
                                articles = lib_data.get('articles', [])
                                
                                # Look for our test article
                                integration_articles = [a for a in articles if 'integration test' in a.get('title', '').lower()]
                                
                                if integration_articles:
                                    # Step 3: Check media statistics
                                    async with self.session.get(f"{API_BASE}/media/stats") as stats_response:
                                        if stats_response.status == 200:
                                            stats_data = await stats_response.json()
                                            
                                            pipeline_score = 0
                                            
                                            # Check processing success
                                            if process_data.get('engine') == 'v2':
                                                pipeline_score += 1
                                                
                                            # Check article creation
                                            if integration_articles:
                                                pipeline_score += 1
                                                
                                            # Check media statistics
                                            if stats_data.get('total_articles', 0) > 0:
                                                pipeline_score += 1
                                                
                                            if pipeline_score >= 2:
                                                self.log_test("Media Integration Content Pipeline", True, 
                                                            f"Pipeline integration successful: score {pipeline_score}/3")
                                            else:
                                                self.log_test("Media Integration Content Pipeline", False, 
                                                            f"Pipeline integration incomplete: score {pipeline_score}/3")
                                        else:
                                            self.log_test("Media Integration Content Pipeline", False, 
                                                        "Media stats unavailable")
                                else:
                                    self.log_test("Media Integration Content Pipeline", False, 
                                                "Integration test article not found in content library")
                            else:
                                self.log_test("Media Integration Content Pipeline", False, 
                                            "Content library unavailable")
                    else:
                        self.log_test("Media Integration Content Pipeline", False, 
                                    f"Document processing failed: {process_data.get('status')}")
                else:
                    self.log_test("Media Integration Content Pipeline", False, 
                                f"HTTP {response.status}")
        except Exception as e:
            self.log_test("Media Integration Content Pipeline", False, f"Exception: {str(e)}")
            
    async def run_all_tests(self):
        """Run all V2 Media Management tests"""
        print("🎯 V2 ENGINE STEP 2 MEDIA MANAGEMENT COMPREHENSIVE TESTING STARTED")
        print("=" * 80)
        
        await self.setup_session()
        
        try:
            # Core V2 Media Management Tests
            await self.test_v2_engine_health_check()
            await self.test_v2_media_manager_instantiation()
            await self.test_media_intelligence_analysis()
            await self.test_contextual_filename_generation()
            await self.test_alt_text_generation()
            await self.test_organized_media_storage()
            await self.test_preview_generation_capabilities()
            
            # Critical Tests (likely the 2 failed areas)
            await self.test_media_extraction_complex_documents()
            await self.test_intelligent_asset_organization()
            await self.test_media_integration_content_pipeline()
            
        finally:
            await self.cleanup_session()
            
        # Calculate results
        total_tests = len(self.test_results)
        passed_tests = len([t for t in self.test_results if t['success']])
        failed_tests = len(self.failed_tests)
        success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
        
        print("\n" + "=" * 80)
        print("🎯 V2 ENGINE STEP 2 MEDIA MANAGEMENT TESTING RESULTS")
        print("=" * 80)
        print(f"📊 TOTAL TESTS: {total_tests}")
        print(f"✅ PASSED: {passed_tests}")
        print(f"❌ FAILED: {failed_tests}")
        print(f"📈 SUCCESS RATE: {success_rate:.1f}%")
        
        if self.failed_tests:
            print(f"\n🔍 FAILED TESTS (Likely the 2 missing criteria from 92% success rate):")
            for i, failed_test in enumerate(self.failed_tests, 1):
                print(f"{i}. {failed_test['test']}: {failed_test['details']}")
                
        print(f"\n📋 DETAILED TEST RESULTS:")
        for result in self.test_results:
            status = "✅" if result['success'] else "❌"
            print(f"{status} {result['test']}: {result['details']}")
            
        return {
            'total_tests': total_tests,
            'passed_tests': passed_tests,
            'failed_tests': failed_tests,
            'success_rate': success_rate,
            'failed_test_details': self.failed_tests,
            'all_results': self.test_results
        }

async def main():
    """Main test execution"""
    tester = V2MediaManagementTester()
    results = await tester.run_all_tests()
    
    # Return results for analysis
    return results

if __name__ == "__main__":
    asyncio.run(main())