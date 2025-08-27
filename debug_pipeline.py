#!/usr/bin/env python3
"""
Debug script to test V2 pipeline directly
"""

import sys
import os
import asyncio
import traceback

# Add app to Python path
sys.path.insert(0, '/app')

async def test_pipeline():
    try:
        print("🔍 Testing V2 Pipeline Import...")
        
        # Test engine imports
        from engine.v2.pipeline import Pipeline, get_pipeline
        print("✅ Pipeline import successful")
        
        # Test pipeline creation
        pipeline = get_pipeline()
        print("✅ Pipeline creation successful")
        print(f"Pipeline type: {type(pipeline)}")
        
        # Test simple pipeline run
        print("🚀 Testing pipeline run...")
        
        test_content = """
        # Simple Test Content
        
        This is a test document for the V2 pipeline.
        
        ## Introduction
        The V2 pipeline should process this content through all 17 stages.
        
        ## Features
        - Content extraction
        - Analysis
        - Article generation
        - Validation
        - Publishing
        """
        
        test_metadata = {
            "title": "Test Document",
            "type": "markdown"
        }
        
        job_id = "test_job_123"
        
        # Run pipeline
        articles, qa_report, version_id = await pipeline.run(job_id, test_content, test_metadata)
        
        print(f"✅ Pipeline run successful!")
        print(f"   Articles generated: {len(articles)}")
        print(f"   QA Report: {type(qa_report)}")
        print(f"   Version ID: {version_id}")
        
        return True
        
    except Exception as e:
        print(f"❌ Pipeline test failed: {e}")
        print("Full traceback:")
        traceback.print_exc()
        return False

if __name__ == "__main__":
    result = asyncio.run(test_pipeline())
    sys.exit(0 if result else 1)