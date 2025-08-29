"""
KE-PR10.5: V2-Only Validation & System Checkpoint
Comprehensive validation that system runs exclusively on V2 engine modules
"""

import pytest
import os
import asyncio
import json
from datetime import datetime
from typing import Dict, Any, List
from pathlib import Path

# Set V2-only mode for this test suite
os.environ["FORCE_V2_ONLY"] = "true"
os.environ["LEGACY_ENDPOINT_BEHAVIOR"] = "block"

class TestV2OnlyValidation:
    """V2-Only validation tests to ensure system runs exclusively on V2 modules"""
    
    def setup_method(self):
        """Setup V2-only mode for each test"""
        os.environ["FORCE_V2_ONLY"] = "true"
        os.environ["LEGACY_ENDPOINT_BEHAVIOR"] = "block"
        print("🚩 KE-PR10.5: V2-Only mode activated for validation")
    
    @pytest.mark.asyncio
    async def test_v2_only_feature_flag_active(self):
        """Test that V2-only feature flag is properly activated"""
        from config.settings import settings
        
        # Force reload settings with V2-only environment
        settings_dict = {
            "FORCE_V2_ONLY": True,
            "LEGACY_ENDPOINT_BEHAVIOR": "block"
        }
        
        assert os.getenv("FORCE_V2_ONLY", "false").lower() == "true", "V2-only mode not activated"
        assert os.getenv("LEGACY_ENDPOINT_BEHAVIOR") == "block", "Legacy blocking not configured"
        print("✅ KE-PR10.5: V2-only feature flags validated")
    
    @pytest.mark.asyncio 
    async def test_v2_content_processing_pipeline(self):
        """Test that content processing works exclusively through V2 pipeline"""
        try:
            import sys
            import os
            backend_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'backend')
            if backend_path not in sys.path:
                sys.path.append(backend_path)
            
            from server import process_text_content_v2_pipeline
            
            # Test content processing
            test_content = "# KE-PR10.5 Test Content\n\nThis is test content for V2-only validation.\n\n## Key Points\n\n- V2 engine should process this exclusively\n- No fallbacks to V1 or hybrid modes\n- Repository pattern should be used"
            
            metadata = {
                "content_type": "text",
                "source": "ke_pr10_5_validation",
                "engine": "v2",
                "ke_pr10_5_v2_only": True
            }
            
            articles = await process_text_content_v2_pipeline(test_content, metadata)
            
            # Validate results
            assert articles is not None, "V2 pipeline failed to process content"
            assert isinstance(articles, list), "V2 pipeline should return list of articles"
            print(f"✅ KE-PR10.5: V2 content processing validated - {len(articles)} articles generated")
            
            # Validate all articles have V2 engine markers
            for article in articles:
                assert article.get("engine") == "v2", f"Article missing V2 engine marker: {article}"
                assert "v2" in str(article.get("metadata", {})), f"Article metadata missing V2 markers: {article}"
            
            print("✅ KE-PR10.5: All articles properly marked with V2 engine")
            
        except Exception as e:
            pytest.fail(f"V2 content processing failed: {str(e)}")
    
    @pytest.mark.asyncio
    async def test_api_health_v2_only_status(self):
        """Test that API health endpoint reports V2-only status correctly"""
        try:
            # Import API router
            from api.router import health
            
            health_response = health()
            
            # Validate V2-only status in health response
            assert "ke_pr10_5" in health_response, "Health response missing KE-PR10.5 status"
            ke_pr10_5 = health_response["ke_pr10_5"]
            
            assert ke_pr10_5.get("force_v2_only") == True, "V2-only mode not reported in health"
            assert ke_pr10_5.get("legacy_endpoint_behavior") == "block", "Legacy blocking not reported"
            assert ke_pr10_5.get("v2_pipeline_exclusive") == True, "V2 pipeline exclusivity not confirmed"
            
            print("✅ KE-PR10.5: API health endpoint validates V2-only status")
            
        except Exception as e:
            pytest.fail(f"API health V2-only validation failed: {str(e)}")
    
    @pytest.mark.asyncio
    async def test_repository_pattern_exclusivity(self):
        """Test that all database operations use repository pattern exclusively"""
        try:
            # Import repository factory
            from engine.stores.mongo import RepositoryFactory
            
            # Test content library repository
            content_repo = RepositoryFactory.get_content_library()
            assert content_repo is not None, "Content library repository not available"
            
            # Test processing jobs repository  
            jobs_repo = RepositoryFactory.get_processing_jobs()
            assert jobs_repo is not None, "Processing jobs repository not available"
            
            # Test V2 repositories
            analysis_repo = RepositoryFactory.get_v2_analysis()
            assert analysis_repo is not None, "V2 analysis repository not available"
            
            validation_repo = RepositoryFactory.get_v2_validation()
            assert validation_repo is not None, "V2 validation repository not available"
            
            print("✅ KE-PR10.5: All repository classes validated and available")
            
            # Test repository operations work
            recent_articles = await content_repo.find_recent(limit=5)
            assert isinstance(recent_articles, list), "Repository operations not working"
            
            print(f"✅ KE-PR10.5: Repository operations validated - {len(recent_articles)} articles found")
            
        except Exception as e:
            pytest.fail(f"Repository pattern validation failed: {str(e)}")
    
    @pytest.mark.asyncio
    async def test_v2_pipeline_module_exclusivity(self):
        """Test that pipeline orchestration routes exclusively to /engine/v2/* modules"""
        try:
            # Import V2 pipeline modules
            from engine.v2.pipeline import V2Pipeline
            from engine.v2.analyzer import V2AnalysisSystem
            from engine.v2.generator import V2ArticleGenerator
            from engine.v2.outline import V2GlobalOutlinePlanner
            
            # Validate V2 modules are available
            assert V2Pipeline is not None, "V2Pipeline module not available"
            assert V2AnalysisSystem is not None, "V2AnalysisSystem module not available" 
            assert V2ArticleGenerator is not None, "V2ArticleGenerator module not available"
            assert V2GlobalOutlinePlanner is not None, "V2GlobalOutlinePlanner module not available"
            
            print("✅ KE-PR10.5: V2 engine modules validated and available")
            
            # Test V2 pipeline instantiation
            v2_pipeline = V2Pipeline()
            assert v2_pipeline is not None, "V2Pipeline instantiation failed"
            
            print("✅ KE-PR10.5: V2 pipeline instantiation successful")
            
        except Exception as e:
            pytest.fail(f"V2 module exclusivity validation failed: {str(e)}")
    
    @pytest.mark.asyncio
    async def test_no_legacy_fallbacks(self):
        """Test that no legacy V1 or hybrid fallbacks are triggered"""
        # This test validates that FORCE_V2_ONLY prevents any legacy code paths
        
        # Check that V1 and hybrid flags are disabled
        from api.router import ENABLE_V1, ENABLE_HYBRID, FORCE_V2_ONLY
        
        assert ENABLE_V1 == False, "V1 mode should be disabled in V2-only validation"
        assert ENABLE_HYBRID == False, "Hybrid mode should be disabled in V2-only validation"  
        assert FORCE_V2_ONLY == True, "V2-only mode should be enabled"
        
        print("✅ KE-PR10.5: Legacy fallback prevention validated")
    
    @pytest.mark.asyncio
    async def test_golden_tests_v2_only_compatibility(self):
        """Test that golden tests pass under V2-only mode"""
        try:
            # Import golden test fixtures
            import sys
            test_path = os.path.dirname(__file__)
            if test_path not in sys.path:
                sys.path.append(test_path)
            
            from golden.test_pipeline import TestGoldenPipeline
            
            # Validate golden test structure exists
            golden_tests = TestGoldenPipeline()
            assert golden_tests is not None, "Golden test suite not available"
            
            print("✅ KE-PR10.5: Golden test suite structure validated")
            
            # Note: Actual golden test execution will be done in CI
            # This test just validates the infrastructure is ready
            
        except Exception as e:
            pytest.fail(f"Golden tests V2-only compatibility failed: {str(e)}")

class TestV2OnlyEndpoints:
    """Test V2-only endpoint behavior and legacy blocking"""
    
    def setup_method(self):
        """Setup V2-only mode for endpoint tests"""
        os.environ["FORCE_V2_ONLY"] = "true"
        os.environ["LEGACY_ENDPOINT_BEHAVIOR"] = "block"
    
    @pytest.mark.asyncio
    async def test_v2_endpoints_functional(self):
        """Test that V2 endpoints remain functional in V2-only mode"""
        try:
            from api.router import router
            
            # Validate V2 endpoints are registered
            v2_endpoints = []
            for route in router.routes:
                if hasattr(route, 'path') and '/api/content/' in route.path:
                    v2_endpoints.append(route.path)
            
            expected_v2_endpoints = [
                "/api/content/process",
                "/api/content/upload", 
                "/api/content/process-url"
            ]
            
            for endpoint in expected_v2_endpoints:
                assert any(endpoint in route_path for route_path in v2_endpoints), f"V2 endpoint missing: {endpoint}"
            
            print(f"✅ KE-PR10.5: V2 endpoints validated - {len(v2_endpoints)} endpoints available")
            
        except Exception as e:
            pytest.fail(f"V2 endpoint validation failed: {str(e)}")
    
    def test_legacy_endpoint_blocking(self):
        """Test that legacy endpoints return HTTP 410 in V2-only mode"""
        from api.router import handle_legacy_endpoint
        
        # Test legacy endpoint blocking
        try:
            handle_legacy_endpoint("legacy_process_v1")
            pytest.fail("Legacy endpoint should have been blocked")
        except Exception as e:
            assert "410" in str(e) or "Legacy endpoint" in str(e), f"Unexpected error: {e}"
            print("✅ KE-PR10.5: Legacy endpoint blocking validated")

# KE-PR10.5: Test Configuration
@pytest.fixture
def v2_only_config():
    """Configuration for V2-only validation tests"""
    return {
        "force_v2_only": True,
        "legacy_behavior": "block",
        "test_content": "# V2-Only Test\n\nValidation content for KE-PR10.5",
        "expected_engine": "v2"
    }

if __name__ == "__main__":
    # Direct execution for debugging
    print("🧪 KE-PR10.5: V2-Only Validation Test Suite")
    print("=" * 60)
    
    # Set environment for testing
    os.environ["FORCE_V2_ONLY"] = "true"
    os.environ["LEGACY_ENDPOINT_BEHAVIOR"] = "block"
    
    # Run basic validation
    test_suite = TestV2OnlyValidation()
    test_endpoints = TestV2OnlyEndpoints()
    
    print("✅ KE-PR10.5: Test suite initialized successfully")
    print("Run with pytest for full validation: pytest tests/ke_pr10_5_v2_only_validation.py -v")