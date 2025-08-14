#!/usr/bin/env python3
"""
Debug DOCX Title Generation Issue
Test the LLM response to understand why "Comprehensive Guide" titles are being generated
"""

import requests
import json
import time
import os
from datetime import datetime

# Configuration
BACKEND_URL = "https://smartdocs-23.preview.emergentagent.com"

def debug_title_generation():
    """Debug the title generation by examining the LLM processing"""
    
    print("🔍 DEBUGGING TITLE GENERATION ISSUE")
    print("=" * 50)
    
    # Test with a simple content that should have a clear title
    test_content = """<h1><a id="_y5kpo0hmift9"></a>Using Google Map Javascript API</h1>
<h2><a id="_gd6syv5bj3yx"></a>Introduction</h2>
<p>This tutorial demonstrates how to build a basic Google Map using its JavaScript API.</p>
<h2><a id="_roa4fy3uktvd"></a>Objective</h2>
<p>To create a map and add a custom marker that points to the Google India office in Bangalore.</p>"""
    
    print(f"📝 Test content preview:")
    print(test_content[:200] + "...")
    print()
    
    # Simulate the LLM call that happens in create_single_article_from_content
    system_message = """You are a professional technical content writer. Generate ONLY clean HTML suitable for WYSIWYG editor display.

CRITICAL REQUIREMENTS:
1. Use ONLY HTML tags: <h1>, <h2>, <h3>, <h4>, <p>, <ul>, <ol>, <li>, <strong>, <em>, <blockquote>, <table>, <thead>, <tbody>, <tr>, <th>, <td>, <code>, <pre>
2. NEVER use Markdown syntax (no ##, **, [], (), ```, ---)
3. Create proper heading hierarchy starting with <h1>
4. Structure content professionally with clear sections
5. NO IMAGES in content (images are managed separately in Asset Library)
6. Generate clean, editor-compatible HTML that renders properly

Respond with valid JSON containing title and HTML content."""
    
    user_message = f"""Transform this complete document into a comprehensive, well-structured article with professional HTML formatting:

CONTENT:
{test_content}

REQUIREMENTS:
1. Create a descriptive title based on the main topic/document title
2. Structure content with proper HTML heading hierarchy (<h1>, <h2>, <h3>)
3. Use appropriate HTML tags for formatting (paragraphs, lists, emphasis, tables)
4. Ensure content is comprehensive and well-organized
5. NO image tags - images are handled separately in Asset Library
6. Generate clean HTML suitable for WYSIWYG editor
7. Preserve all important information from the source content

RESPONSE FORMAT:
{{
    "title": "Descriptive title for the complete article",
    "content": "<h1>Title</h1><p>Introduction paragraph...</p><h2>Section Header</h2><p>Content...</p>",
    "summary": "Brief summary of what this article covers",
    "tags": ["topic1", "topic2", "topic3"],
    "takeaways": ["Key point 1", "Key point 2", "Key point 3"]
}}"""
    
    print("🤖 Testing LLM response for title generation...")
    print("System message preview:", system_message[:100] + "...")
    print("User message preview:", user_message[:200] + "...")
    print()
    
    # Test the AI assistance endpoint directly
    try:
        response = requests.post(
            f"{BACKEND_URL}/api/ai-assistance",
            json={
                "system_message": system_message,
                "user_message": user_message,
                "session_id": "debug_title_test"
            },
            timeout=60
        )
        
        if response.status_code == 200:
            result = response.json()
            ai_response = result.get('response', '')
            
            print("✅ LLM Response received:")
            print("-" * 30)
            print(ai_response)
            print("-" * 30)
            print()
            
            # Try to parse the JSON response
            try:
                import re
                json_match = re.search(r'```json\s*(.*?)\s*```', ai_response, re.DOTALL | re.IGNORECASE)
                if json_match:
                    json_str = json_match.group(1)
                else:
                    json_str = ai_response
                
                article_data = json.loads(json_str)
                
                print("📋 PARSED RESPONSE:")
                print(f"Title: '{article_data.get('title', 'NO TITLE')}'")
                print(f"Content preview: {article_data.get('content', 'NO CONTENT')[:200]}...")
                print(f"Summary: {article_data.get('summary', 'NO SUMMARY')}")
                print(f"Tags: {article_data.get('tags', [])}")
                print()
                
                # Analyze the title
                generated_title = article_data.get('title', '')
                print("🔍 TITLE ANALYSIS:")
                
                if "comprehensive guide" in generated_title.lower():
                    print("❌ ISSUE CONFIRMED: LLM is generating 'Comprehensive Guide' titles")
                    print("   This suggests the LLM prompt is encouraging generic titles")
                elif "using google map javascript api" in generated_title.lower():
                    print("✅ GOOD: Title matches the source H1 heading")
                else:
                    print(f"⚠️ UNEXPECTED: Title doesn't match expected patterns: '{generated_title}'")
                
                # Check if the original H1 is preserved in content
                content = article_data.get('content', '')
                if "Using Google Map Javascript API" in content:
                    print("✅ Original H1 preserved in content")
                else:
                    print("❌ Original H1 not preserved in content")
                
            except json.JSONDecodeError as e:
                print(f"❌ JSON parsing failed: {e}")
                print("Raw response:", ai_response[:500])
            
        else:
            print(f"❌ LLM request failed: {response.status_code}")
            print(f"Response: {response.text}")
            
    except Exception as e:
        print(f"❌ Debug test failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    debug_title_generation()