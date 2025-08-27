#!/usr/bin/env python3
"""
KE-PR3 Tests: Verify media intelligence extraction and assets store
Tests for media module isolation and file I/O abstraction
"""

import sys
import os
import tempfile

# Add app root to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_assets_store():
    """Test assets store basic functionality"""
    print("🧪 Testing assets store...")
    
    try:
        from engine.stores.assets import save_bytes, save_file, read_file, get_asset_path, hash_bytes
        
        # Test content hashing
        test_data = b"Hello, World!"
        content_hash = hash_bytes(test_data)
        
        if len(content_hash) == 16:  # SHA256[:16]
            print(f"  ✅ Content hash generated: {content_hash}")
        else:
            print(f"  ❌ Invalid hash length: {len(content_hash)}")
            return False
        
        # Test save_bytes with temp directory
        with tempfile.TemporaryDirectory() as temp_dir:
            hash_result, filename = save_bytes(test_data, "test.txt", temp_dir)
            
            if hash_result == content_hash and filename.startswith(content_hash):
                print(f"  ✅ save_bytes: {filename}")
            else:
                print(f"  ❌ save_bytes failed: hash={hash_result}, file={filename}")
                return False
            
            # Test file exists and content matches
            full_path = get_asset_path(filename, temp_dir)
            if os.path.exists(full_path):
                print(f"  ✅ File created at: {full_path}")
            else:
                print(f"  ❌ File not found: {full_path}")
                return False
            
            # Test read_file
            read_data = read_file(full_path)
            if read_data == test_data:
                print(f"  ✅ read_file: {len(read_data)} bytes")
            else:
                print(f"  ❌ read_file mismatch: {read_data} != {test_data}")
                return False
            
            # Test deduplication (save same content again)
            hash2, filename2 = save_bytes(test_data, "test2.txt", temp_dir)
            if hash2 == content_hash and filename2 == filename:
                print(f"  ✅ Deduplication works: {filename2}")
            else:
                print(f"  ❌ Deduplication failed: {filename2} != {filename}")
                return False
        
        print("✅ Assets store tests passed")
        return True
        
    except Exception as e:
        print(f"❌ Assets store test failed: {e}")
        return False


def test_media_intelligence_import():
    """Test media intelligence module imports"""
    print("🧪 Testing media intelligence imports...")
    
    try:
        from engine.media import media_intelligence, MediaIntelligenceService
        
        # Check that service is properly instantiated
        if hasattr(media_intelligence, 'analyze_media_comprehensive'):
            print("  ✅ media_intelligence service available")
        else:
            print("  ❌ media_intelligence service missing methods")
            return False
        
        # Check class import
        service = MediaIntelligenceService()
        if hasattr(service, 'analyze_media_comprehensive'):
            print("  ✅ MediaIntelligenceService class works")
        else:
            print("  ❌ MediaIntelligenceService class missing methods")
            return False
        
        print("✅ Media intelligence import tests passed")
        return True
        
    except Exception as e:
        print(f"❌ Media intelligence import test failed: {e}")
        return False


def test_legacy_media_import():
    """Test legacy media module import"""
    print("🧪 Testing legacy media import...")
    
    try:
        from engine.media.legacy import MediaIntelligenceService as LegacyService
        
        legacy_service = LegacyService()
        if hasattr(legacy_service, 'analyze_media_comprehensive'):
            print("  ✅ Legacy media service available")
        else:
            print("  ❌ Legacy media service missing methods")
            return False
        
        print("✅ Legacy media import tests passed")
        return True
        
    except Exception as e:
        print(f"❌ Legacy media import test failed: {e}")
        return False


def test_server_integration():
    """Test that server can import new media modules"""
    print("🧪 Testing server integration...")
    
    try:
        # Add backend to path
        sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))
        
        # Test server import
        from server import app
        print("  ✅ Server imports successfully")
        
        # Test that media_intelligence is available in server context
        import server
        if hasattr(server, 'media_intelligence'):
            print("  ✅ media_intelligence available in server")
        else:
            print("  ❌ media_intelligence not found in server")
            return False
        
        print("✅ Server integration tests passed")
        return True
        
    except Exception as e:
        print(f"❌ Server integration test failed: {e}")
        return False


def test_file_operations_abstraction():
    """Test that assets store handles various file operations"""
    print("🧪 Testing file operations abstraction...")
    
    try:
        from engine.stores.assets import save_bytes, get_file_info, list_assets, copy_asset
        
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create test files
            test_files = [
                (b"Image data", "image.png"),
                (b"Document content", "document.pdf"),
                (b"Video data", "video.mp4")
            ]
            
            saved_files = []
            for data, filename in test_files:
                hash_result, relative_path = save_bytes(data, filename, temp_dir)
                saved_files.append(relative_path)
                print(f"  ✅ Saved: {relative_path}")
            
            # Test list_assets
            assets = list_assets(temp_dir)
            if len(assets) == len(test_files):
                print(f"  ✅ Listed {len(assets)} assets")
            else:
                print(f"  ❌ Asset count mismatch: {len(assets)} != {len(test_files)}")
                return False
            
            # Test get_file_info
            info = get_file_info(os.path.join(temp_dir, saved_files[0]))
            if info.get('exists') and 'hash' in info and 'size' in info:
                print(f"  ✅ File info: {info['size']} bytes, hash {info['hash']}")
            else:
                print(f"  ❌ Invalid file info: {info}")
                return False
        
        print("✅ File operations abstraction tests passed")
        return True
        
    except Exception as e:
        print(f"❌ File operations test failed: {e}")
        return False


def test_media_endpoint_compatibility():
    """Test that media endpoints still work with extracted modules"""
    print("🧪 Testing media endpoint compatibility...")
    
    try:
        # This is a basic import/structure test since we can't easily test async endpoints
        from engine.media.intelligence import MediaIntelligenceService
        
        service = MediaIntelligenceService()
        
        # Check required methods exist with correct signatures
        methods_to_check = [
            'analyze_media_comprehensive',
            'create_enhanced_media_html', 
            'generate_contextual_placement'
        ]
        
        for method_name in methods_to_check:
            if hasattr(service, method_name):
                method = getattr(service, method_name)
                if callable(method):
                    print(f"  ✅ Method available: {method_name}")
                else:
                    print(f"  ❌ Method not callable: {method_name}")
                    return False
            else:
                print(f"  ❌ Method missing: {method_name}")
                return False
        
        print("✅ Media endpoint compatibility tests passed")
        return True
        
    except Exception as e:
        print(f"❌ Media endpoint compatibility test failed: {e}")
        return False


if __name__ == "__main__":
    print("🧪 Running KE-PR3 Media Intelligence & Assets Store Tests...")
    print("=" * 70)
    
    tests = [
        test_assets_store,
        test_media_intelligence_import,
        test_legacy_media_import,
        test_server_integration,
        test_file_operations_abstraction,
        test_media_endpoint_compatibility
    ]
    
    passed = 0
    for test in tests:
        try:
            if test():
                passed += 1
            print()  # Add spacing between tests
        except Exception as e:
            print(f"❌ Test {test.__name__} crashed: {e}")
            print()
    
    print("=" * 70)
    print(f"📊 Test Results: {passed}/{len(tests)} tests passed")
    
    if passed == len(tests):
        print("🎉 KE-PR3 media intelligence extraction is working correctly!")
        print("✅ Media modules isolated and assets store functional")
        exit(0)
    else:
        print("❌ KE-PR3 media intelligence extraction has issues")
        exit(1)