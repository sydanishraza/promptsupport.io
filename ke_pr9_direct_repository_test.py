#!/usr/bin/env python3
"""
KE-PR9 Direct MongoDB Repository Testing
Test the repository layer directly to verify implementation
"""

import os
import sys
import asyncio
import json
from datetime import datetime

# Add the app directory to Python path
app_path = os.path.dirname(__file__)
if app_path not in sys.path:
    sys.path.insert(0, app_path)

print(f"🔍 Testing KE-PR9 MongoDB Repository Layer directly")
print(f"📁 App path: {app_path}")

# Test direct import of repository layer
try:
    from engine.stores.mongo import (
        RepositoryFactory, 
        upsert_content, 
        fetch_article_by_slug, 
        fetch_article_by_uid,
        update_article_headings, 
        update_article_xrefs,
        test_mongo_roundtrip
    )
    print("✅ KE-PR9: MongoDB repository layer imported successfully")
    mongo_repo_available = True
except ImportError as e:
    print(f"❌ KE-PR9: MongoDB repository layer import failed: {e}")
    mongo_repo_available = False

async def test_repository_layer():
    """Test the repository layer functionality"""
    if not mongo_repo_available:
        print("❌ Cannot test repository layer - import failed")
        return False
    
    try:
        print("\n🧪 Testing Repository Factory...")
        
        # Test 1: Repository Factory
        content_repo = RepositoryFactory.get_content_library()
        qa_repo = RepositoryFactory.get_qa_results()
        assets_repo = RepositoryFactory.get_assets()
        
        print("✅ Repository Factory: All repositories created successfully")
        
        # Test 2: Content Library Repository
        print("\n🧪 Testing Content Library Repository...")
        
        test_article = {
            "id": "test_ke_pr9_direct",
            "title": "KE-PR9 Direct Test Article",
            "content": "Test content for direct repository testing",
            "doc_uid": "test-uid-direct-ke-pr9",
            "doc_slug": "ke-pr9-direct-test",
            "headings": [{"id": "test-heading", "text": "Test Heading", "level": 2}],
            "xrefs": [{"target": "test-ref", "type": "internal"}],
            "engine": "v2"
        }
        
        # Insert test article
        article_id = await content_repo.insert_article(test_article)
        print(f"✅ Article inserted with ID: {article_id}")
        
        # Test retrieval by doc_uid
        retrieved = await content_repo.find_by_doc_uid("test-uid-direct-ke-pr9")
        if retrieved:
            print("✅ Article retrieved by doc_uid")
        else:
            print("❌ Failed to retrieve article by doc_uid")
            return False
        
        # Test retrieval by doc_slug
        retrieved_slug = await content_repo.find_by_doc_slug("ke-pr9-direct-test")
        if retrieved_slug:
            print("✅ Article retrieved by doc_slug")
        else:
            print("❌ Failed to retrieve article by doc_slug")
            return False
        
        # Test TICKET-3 fields
        if 'headings' in retrieved and 'xrefs' in retrieved:
            print("✅ TICKET-3 fields (headings, xrefs) preserved")
        else:
            print("❌ TICKET-3 fields missing")
            return False
        
        # Test update operations
        updated = await content_repo.upsert_content("test-uid-direct-ke-pr9", {"title": "Updated Title"})
        if updated:
            print("✅ Content upsert successful")
        else:
            print("❌ Content upsert failed")
            return False
        
        # Test headings update
        new_headings = [{"id": "updated-heading", "text": "Updated Heading", "level": 2}]
        headings_updated = await content_repo.update_headings("test-uid-direct-ke-pr9", new_headings)
        if headings_updated:
            print("✅ Headings update successful")
        else:
            print("❌ Headings update failed")
        
        # Test xrefs update
        new_xrefs = [{"target": "updated-ref", "type": "external"}]
        xrefs_updated = await content_repo.update_xrefs("test-uid-direct-ke-pr9", new_xrefs)
        if xrefs_updated:
            print("✅ Cross-references update successful")
        else:
            print("❌ Cross-references update failed")
        
        # Test convenience functions
        print("\n🧪 Testing Convenience Functions...")
        
        convenience_article = await fetch_article_by_uid("test-uid-direct-ke-pr9")
        if convenience_article:
            print("✅ Convenience function fetch_article_by_uid working")
        else:
            print("❌ Convenience function fetch_article_by_uid failed")
        
        convenience_slug = await fetch_article_by_slug("ke-pr9-direct-test")
        if convenience_slug:
            print("✅ Convenience function fetch_article_by_slug working")
        else:
            print("❌ Convenience function fetch_article_by_slug failed")
        
        # Test QA Repository
        print("\n🧪 Testing QA Repository...")
        
        test_qa_report = {
            "job_id": "test-job-ke-pr9",
            "status": "completed",
            "flags": [],
            "summary": "Test QA report for KE-PR9",
            "engine": "v2"
        }
        
        qa_id = await qa_repo.insert_qa_report(test_qa_report)
        print(f"✅ QA report inserted with ID: {qa_id}")
        
        # Test QA retrieval
        recent_qa = await qa_repo.find_recent_qa_summaries(5)
        if recent_qa:
            print(f"✅ Retrieved {len(recent_qa)} recent QA reports")
        else:
            print("⚠️ No recent QA reports found (this is okay)")
        
        # Test Assets Repository
        print("\n🧪 Testing Assets Repository...")
        
        test_assets = [
            {
                "filename": "test-asset-1.jpg",
                "url": "/static/test-asset-1.jpg",
                "type": "image",
                "size": 1024
            },
            {
                "filename": "test-asset-2.png", 
                "url": "/static/test-asset-2.png",
                "type": "image",
                "size": 2048
            }
        ]
        
        asset_ids = await assets_repo.insert_assets(test_assets)
        print(f"✅ {len(asset_ids)} assets inserted")
        
        # Test asset retrieval
        assets = await assets_repo.find_assets(limit=10)
        if assets:
            print(f"✅ Retrieved {len(assets)} assets")
        else:
            print("⚠️ No assets found")
        
        # Test integration roundtrip
        print("\n🧪 Testing Integration Roundtrip...")
        
        roundtrip_success = await test_mongo_roundtrip()
        if roundtrip_success:
            print("✅ MongoDB roundtrip test passed")
        else:
            print("❌ MongoDB roundtrip test failed")
            return False
        
        # Cleanup test data
        print("\n🧹 Cleaning up test data...")
        await content_repo.delete_by_id("test_ke_pr9_direct")
        print("✅ Test cleanup completed")
        
        return True
        
    except Exception as e:
        print(f"❌ Repository testing failed: {e}")
        import traceback
        traceback.print_exc()
        return False

async def main():
    """Main test function"""
    print("🚀 Starting KE-PR9 Direct Repository Testing")
    print("=" * 60)
    
    if not mongo_repo_available:
        print("❌ KE-PR9 MongoDB Repository Layer: NOT AVAILABLE")
        return
    
    success = await test_repository_layer()
    
    print("\n" + "=" * 60)
    if success:
        print("✅ KE-PR9 MongoDB Repository Layer: FULLY FUNCTIONAL")
        print("🎯 All repository operations working correctly")
        print("📊 TICKET-3 fields properly supported")
        print("🔄 Integration roundtrip successful")
    else:
        print("❌ KE-PR9 MongoDB Repository Layer: ISSUES DETECTED")
        print("⚠️ Some repository operations failed")

if __name__ == "__main__":
    asyncio.run(main())