#!/usr/bin/env python3
"""
Direct Pipeline Test - Test the V2 pipeline directly without HTTP
"""

import sys
import os
import asyncio

# Add parent directory to Python path for engine package
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

try:
    from engine.v2.pipeline import Pipeline, get_pipeline
    from engine.v2.analyzer import V2MultiDimensionalAnalyzer
    from engine.v2.review import V2ReviewSystem
    from engine.v2.versioning import V2VersioningSystem
    print("✅ Successfully imported V2 classes")
except ImportError as e:
    print(f"❌ Import failed: {e}")
    sys.exit(1)

async def test_pipeline_direct():
    """Test the pipeline directly"""
    try:
        print("🚀 Testing V2 Pipeline directly...")
        
        # Test V2ReviewSystem method availability
        review_system = V2ReviewSystem()
        print(f"✅ V2ReviewSystem created: {type(review_system)}")
        print(f"✅ Has enqueue_for_review method: {hasattr(review_system, 'enqueue_for_review')}")
        
        # Test V2VersioningSystem method availability  
        versioning_system = V2VersioningSystem()
        print(f"✅ V2VersioningSystem created: {type(versioning_system)}")
        print(f"✅ Has create_version_from_articles method: {hasattr(versioning_system, 'create_version_from_articles')}")
        
        # Test pipeline creation
        pipeline = get_pipeline()
        print(f"✅ Pipeline created: {type(pipeline)}")
        print(f"✅ Pipeline reviewer type: {type(pipeline.reviewer)}")
        print(f"✅ Pipeline versioning type: {type(pipeline.versioning)}")
        
        # Test simple content processing
        test_content = "# Test Content\n\nThis is a simple test."
        test_metadata = {"title": "Test Article", "content_type": "markdown"}
        
        print("🔄 Running pipeline...")
        articles, qa_report, version_id = await pipeline.run("test_job", test_content, test_metadata)
        
        print(f"✅ Pipeline completed successfully!")
        print(f"   Articles: {len(articles)}")
        print(f"   Version ID: {version_id}")
        print(f"   QA Report: {type(qa_report)}")
        
        return True
        
    except Exception as e:
        print(f"❌ Pipeline test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = asyncio.run(test_pipeline_direct())
    sys.exit(0 if success else 1)