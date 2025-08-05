#!/usr/bin/env python3
"""
Direct LLM Test for Title Generation Issue
Test the call_llm_with_fallback function directly to see what's happening
"""

import asyncio
import sys
import os

# Add the backend directory to the path so we can import the functions
sys.path.append('/app/backend')

async def test_llm_title_generation():
    """Test the LLM directly to see what title it generates"""
    
    print("🔍 DIRECT LLM TITLE GENERATION TEST")
    print("=" * 50)
    
    # Import the LLM function from the backend
    try:
        # We need to set up the environment first
        os.environ['OPENAI_API_KEY'] = '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'
        os.environ['ANTHROPIC_API_KEY'] = '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'
        
        # Import the function
        import requests
        import json
        
        # Test content with clear H1 title
        test_content = """<h1><a id="_y5kpo0hmift9"></a>Using Google Map Javascript API</h1>
<h2><a id="_gd6syv5bj3yx"></a>Introduction</h2>
<p>This tutorial demonstrates how to build a basic Google Map using its JavaScript API.</p>
<h2><a id="_roa4fy3uktvd"></a>Objective</h2>
<p>To create a map and add a custom marker that points to the Google India office in Bangalore.</p>
<h2><a id="_q7rebzzg94h3"></a>Summary</h2>
<p>This tutorial contains three steps to achieve the objective:</p>
<ol>
<li>Create an HTML page.</li>
<li>Add a map with a custom marker.</li>
<li>Authenticate the map using the API key.</li>
</ol>"""
        
        print(f"📝 Test content (first H1): 'Using Google Map Javascript API'")
        print(f"📊 Content length: {len(test_content)} characters")
        print()
        
        # Test with OpenAI directly
        print("🤖 Testing OpenAI API directly...")
        
        system_message = """You are a professional technical content writer. Generate ONLY clean HTML suitable for WYSIWYG editor display.

CRITICAL REQUIREMENTS:
1. Use ONLY HTML tags: <h1>, <h2>, <h3>, <h4>, <p>, <ul>, <ol>, <li>, <strong>, <em>, <blockquote>, <table>, <thead>, <tbody>, <tr>, <th>, <td>, <code>, <pre>
2. NEVER use Markdown syntax (no ##, **, [], (), ```, ---)
3. Create proper heading hierarchy starting with <h1>
4. Structure content professionally with clear sections
5. NO IMAGES in content (images are managed separately in Asset Library)
6. Generate clean, editor-compatible HTML that renders properly

IMPORTANT: PRESERVE THE ORIGINAL TITLE PROVIDED. Do NOT create generic titles like "Comprehensive Guide to..." or similar. Use the exact title provided in the user message.

Respond with valid JSON containing title and HTML content."""
        
        user_message = f"""Transform this complete document into a comprehensive, well-structured article with professional HTML formatting:

CONTENT:
{test_content}

REQUIREMENTS:
1. PRESERVE THE ORIGINAL TITLE: The document title is "Using Google Map Javascript API" - use this EXACT title
2. Structure content with proper HTML heading hierarchy (<h1>, <h2>, <h3>)
3. Use appropriate HTML tags for formatting (paragraphs, lists, emphasis, tables)
4. Ensure content is comprehensive and well-organized
5. NO image tags - images are handled separately in Asset Library
6. Generate clean HTML suitable for WYSIWYG editor
7. Preserve all important information from the source content

RESPONSE FORMAT:
{{
    "title": "Using Google Map Javascript API",
    "content": "<h1>Using Google Map Javascript API</h1><p>Introduction paragraph...</p><h2>Section Header</h2><p>Content...</p>",
    "summary": "Brief summary of what this article covers",
    "tags": ["Google Maps", "JavaScript", "API"],
    "takeaways": ["Key point 1", "Key point 2", "Key point 3"]
}}"""
        
        # Make direct OpenAI API call
        openai_headers = {
            'Authorization': f'Bearer {os.environ["OPENAI_API_KEY"]}',
            'Content-Type': 'application/json'
        }
        
        openai_payload = {
            'model': 'gpt-4o-mini',
            'messages': [
                {'role': 'system', 'content': system_message},
                {'role': 'user', 'content': user_message}
            ],
            'max_tokens': 2000,
            'temperature': 0.3
        }
        
        response = requests.post(
            'https://api.openai.com/v1/chat/completions',
            headers=openai_headers,
            json=openai_payload,
            timeout=60
        )
        
        if response.status_code == 200:
            result = response.json()
            ai_response = result['choices'][0]['message']['content']
            
            print("✅ OpenAI Response received:")
            print("-" * 40)
            print(ai_response)
            print("-" * 40)
            print()
            
            # Parse the JSON response
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
                print(f"Content preview: {article_data.get('content', 'NO CONTENT')[:300]}...")
                print(f"Summary: {article_data.get('summary', 'NO SUMMARY')}")
                print(f"Tags: {article_data.get('tags', [])}")
                print()
                
                # Analyze the title
                generated_title = article_data.get('title', '')
                print("🔍 TITLE ANALYSIS:")
                
                if "comprehensive guide" in generated_title.lower():
                    print("❌ ISSUE: LLM still generating 'Comprehensive Guide' titles despite explicit instructions")
                elif "using google map javascript api" in generated_title.lower():
                    print("✅ SUCCESS: Title matches the expected 'Using Google Map Javascript API'")
                else:
                    print(f"⚠️ DIFFERENT: Title is different but not 'Comprehensive Guide': '{generated_title}'")
                
                # Check content quality
                content = article_data.get('content', '')
                content_length = len(content)
                
                print(f"\n📖 CONTENT ANALYSIS:")
                print(f"Content length: {content_length} characters")
                
                if content_length < 1000:
                    print("❌ ISSUE: Content appears to be summarized (too short)")
                elif content_length > 2000:
                    print("✅ GOOD: Content appears to be enhanced/comprehensive")
                else:
                    print("⚠️ MODERATE: Content length is moderate")
                
                # Check for enhancement vs summarization
                if "comprehensive" in content.lower() or "detailed" in content.lower():
                    print("✅ Content shows enhancement characteristics")
                elif "summary" in content.lower() or "brief" in content.lower():
                    print("❌ Content shows summarization characteristics")
                
            except json.JSONDecodeError as e:
                print(f"❌ JSON parsing failed: {e}")
                print("Raw response:", ai_response[:500])
                
        else:
            print(f"❌ OpenAI API failed: {response.status_code}")
            print(f"Response: {response.text}")
            
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_llm_title_generation())