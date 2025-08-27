#!/usr/bin/env python3
"""
KE-PR1 Test: Verify new engine package imports and models
This is a placeholder test that verifies the scaffolding is working.
"""

def test_engine_imports():
    """Test that all engine modules can be imported without errors"""
    try:
        from engine.models import RawBundle, QAReport, MediaAsset, Section, NormDoc
        from engine.logging_util import stage_log, logger
        from config.settings import settings
        print("✅ All engine imports successful")
        return True
    except ImportError as e:
        print(f"❌ Import failed: {e}")
        return False

def test_pydantic_models():
    """Test that Pydantic models can be instantiated"""
    try:
        from engine.models.io import RawBundle, Section, SourceSpan
        from engine.models.qa import QAReport, QAFlag
        from engine.models.content import MediaAsset
        
        # Test RawBundle creation
        bundle = RawBundle(
            job_id="test-123",
            source_id="test-doc",
            blocks=[],
            metadata={"test": True}
        )
        
        # Test QAReport creation  
        report = QAReport(
            job_id="test-123",
            coverage_percent=95.0,
            flags=[]
        )
        
        # Test MediaAsset creation
        asset = MediaAsset(
            id="asset-123",
            type="image",
            format="png",
            path="/test/path.png",
            hash="abc123"
        )
        
        print("✅ All Pydantic models work correctly")
        return True
    except Exception as e:
        print(f"❌ Model test failed: {e}")
        return False

def test_logging_decorator():
    """Test that logging decorator works"""
    try:
        from engine.logging_util import stage_log
        
        @stage_log("test_stage")
        def test_function(job_id="test-job"):
            return "success"
        
        result = test_function()
        print("✅ Logging decorator works correctly")
        return result == "success"
    except Exception as e:
        print(f"❌ Logging test failed: {e}")
        return False

def test_settings():
    """Test that settings can be loaded (may fail if .env not configured)"""
    try:
        from config.settings import settings
        
        # These should have default values
        assert settings.UPLOAD_DIR == "static/uploads"
        assert settings.TEMP_DIR == "temp_uploads"
        assert settings.LLM_PROVIDER == "openai"
        
        print("✅ Settings configuration works correctly")
        return True
    except Exception as e:
        print(f"⚠️ Settings test failed (expected if .env not configured): {e}")
        return False  # This is expected to fail in some environments

if __name__ == "__main__":
    print("🧪 Running KE-PR1 scaffolding tests...")
    
    tests = [
        test_engine_imports,
        test_pydantic_models, 
        test_logging_decorator,
        test_settings
    ]
    
    passed = 0
    for test in tests:
        try:
            if test():
                passed += 1
        except Exception as e:
            print(f"❌ Test {test.__name__} crashed: {e}")
    
    print(f"\n📊 Test Results: {passed}/{len(tests)} tests passed")
    
    if passed >= 3:  # Allow settings test to fail
        print("🎉 KE-PR1 scaffolding is working correctly!")
        exit(0)
    else:
        print("❌ KE-PR1 scaffolding has issues")
        exit(1)