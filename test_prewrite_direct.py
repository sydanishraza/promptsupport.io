#!/usr/bin/env python3
"""
Direct test of V2PrewriteSystem to verify functionality
"""

import asyncio
import sys
import os
sys.path.append('/app/backend')

# Import the prewrite system
from server import V2PrewriteSystem

async def test_prewrite_system():
    """Test the prewrite system directly"""
    
    # Create test data
    content = """# Google Maps JavaScript API Integration Guide

## Introduction
This comprehensive guide covers the implementation of Google Maps JavaScript API in web applications. The API provides powerful mapping capabilities for developers.

## Getting Started
To begin using the Google Maps API, you need to obtain an API key from the Google Cloud Console. This key authenticates your application with Google's services.

### API Key Setup
1. Visit the Google Cloud Console
2. Create a new project or select existing
3. Enable the Maps JavaScript API
4. Generate an API key
5. Restrict the key for security

## Basic Map Implementation
The basic implementation requires HTML structure and JavaScript initialization code.

### HTML Structure
```html
<div id="map" style="height: 400px; width: 100%;"></div>
<script src="https://maps.googleapis.com/maps/api/js?key=YOUR_API_KEY&callback=initMap"></script>
```

### JavaScript Implementation
```javascript
function initMap() {
    const map = new google.maps.Map(document.getElementById("map"), {
        zoom: 10,
        center: { lat: -34.397, lng: 150.644 }
    });
}
```

## Advanced Features
Advanced features include markers, info windows, and custom styling options.
"""

    # Create test articles
    articles = [
        {
            "title": "Google Maps JavaScript API Integration Guide",
            "content": content,
            "id": "test_article_1"
        }
    ]
    
    # Create test per-article outlines
    per_article_outlines = {
        "article_0": {
            "sections": [
                {
                    "title": "Introduction",
                    "heading": "Introduction",
                    "content_focus": "Overview of Google Maps API capabilities"
                },
                {
                    "title": "Getting Started", 
                    "heading": "Getting Started",
                    "content_focus": "API key setup and initial configuration"
                },
                {
                    "title": "Basic Map Implementation",
                    "heading": "Basic Map Implementation", 
                    "content_focus": "HTML structure and JavaScript initialization"
                },
                {
                    "title": "Advanced Features",
                    "heading": "Advanced Features",
                    "content_focus": "Markers, info windows, and custom styling"
                }
            ]
        }
    }
    
    # Create test global analysis
    global_analysis = {
        "content_type": "tutorial",
        "audience": "developer",
        "complexity": "intermediate"
    }
    
    # Initialize prewrite system
    prewrite_system = V2PrewriteSystem()
    
    print("🧪 TESTING V2PREWRITESYSTEM DIRECTLY")
    print("=" * 50)
    
    try:
        # Test prewrite execution
        result = await prewrite_system.execute_prewrite_pass(
            content=content,
            content_type="tutorial", 
            articles=articles,
            per_article_outlines=per_article_outlines,
            global_analysis=global_analysis,
            run_id="test_run_123"
        )
        
        print(f"✅ Prewrite Result: {result.get('prewrite_status')}")
        print(f"✅ Articles Processed: {result.get('articles_processed', 0)}")
        print(f"✅ Successful Prewrites: {result.get('successful_prewrites', 0)}")
        print(f"✅ Success Rate: {result.get('success_rate', 0):.1f}%")
        
        # Check prewrite results
        prewrite_results = result.get('prewrite_results', [])
        for i, prewrite_result in enumerate(prewrite_results):
            print(f"\n📄 Article {i+1} Prewrite:")
            print(f"   Status: {prewrite_result.get('prewrite_status')}")
            print(f"   Sections: {prewrite_result.get('sections_processed', 0)}")
            print(f"   Facts: {prewrite_result.get('total_facts_extracted', 0)}")
            
            if prewrite_result.get('prewrite_status') == 'error':
                print(f"   Error: {prewrite_result.get('error')}")
        
        # Check if prewrite files were created
        prewrite_dir = "/app/backend/static/prewrite_data"
        if os.path.exists(prewrite_dir):
            files = [f for f in os.listdir(prewrite_dir) if f.startswith('prewrite_test_run_123')]
            print(f"\n📁 Prewrite Files Created: {len(files)}")
            for file in files:
                print(f"   📄 {file}")
        
        return result.get('prewrite_status') == 'success'
        
    except Exception as e:
        print(f"❌ Direct prewrite test error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = asyncio.run(test_prewrite_system())
    print(f"\n🎯 DIRECT PREWRITE TEST: {'✅ PASSED' if success else '❌ FAILED'}")