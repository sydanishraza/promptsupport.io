"""
KE-PR9: Simple integration test for MongoDB repository layer
"""

import asyncio
from .mongo import test_mongo_roundtrip, RepositoryFactory

async def run_integration_tests():
    """Run simple integration tests for repository layer"""
    print("🧪 KE-PR9: Starting MongoDB repository integration tests...")
    
    try:
        # Test basic roundtrip
        roundtrip_success = await test_mongo_roundtrip()
        
        if not roundtrip_success:
            print("❌ KE-PR9: Basic roundtrip test failed")
            return False
        
        # Test repository factory
        content_repo = RepositoryFactory.get_content_library()
        qa_repo = RepositoryFactory.get_qa_results()
        assets_repo = RepositoryFactory.get_assets()
        
        if not all([content_repo, qa_repo, assets_repo]):
            print("❌ KE-PR9: Repository factory test failed")
            return False
        
        print("✅ KE-PR9: All integration tests passed!")
        return True
        
    except Exception as e:
        print(f"❌ KE-PR9: Integration tests failed: {e}")
        return False

if __name__ == "__main__":
    # Run tests when called directly
    asyncio.run(run_integration_tests())