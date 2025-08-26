#!/usr/bin/env python3
"""
Direct TICKET 2 Implementation Test
Test the TICKET 2 methods directly without API calls
"""

import sys
import os
sys.path.append('/app/backend')

# Import the V2StyleProcessor class
import importlib.util
spec = importlib.util.spec_from_file_location("server", "/app/backend/server.py")
server_module = importlib.util.module_from_spec(spec)

print("🧪 DIRECT TICKET 2 TESTING")
print("=" * 50)

# Test HTML content with headings
test_content = """
<h2>Getting Started with API Integration</h2>
<p>This section covers the basics of API integration.</p>

<h3>API Key & Authentication Setup</h3>
<p>Configure your API credentials for secure access.</p>

<h2>Getting Started with API Integration</h2>
<p>Duplicate heading to test collision handling.</p>

<h3>Special Characters: Testing (Symbols) & Unicode™</h3>
<p>Testing special character handling in slugs.</p>

<h4>Step-by-Step Configuration Process</h4>
<p>Detailed configuration steps and procedures.</p>

<h2>Advanced Topics</h2>
<p>More advanced integration patterns.</p>
"""

try:
    # Load the server module to get the V2StyleProcessor class
    spec.loader.exec_module(server_module)
    
    # Create V2StyleProcessor instance
    processor = server_module.V2StyleProcessor()
    
    print("✅ V2StyleProcessor loaded successfully")
    print()
    
    # Test 1: Stable slug generation
    print("🔧 TEST 1: Stable Slug Generation")
    test_texts = [
        "Getting Started with API Integration",
        "API Key & Authentication Setup", 
        "Special Characters: Testing (Symbols) & Unicode™",
        "Step-by-Step Configuration Process"
    ]
    
    for text in test_texts:
        slug = processor.stable_slug(text)
        print(f"   '{text}' → '{slug}'")
    print()
    
    # Test 2: Heading ID assignment
    print("🔧 TEST 2: Heading ID Assignment")
    content_with_ids = processor.assign_heading_ids(test_content)
    
    # Check if IDs were assigned
    import re
    assigned_ids = re.findall(r'<h[234][^>]*id="([^"]+)"', content_with_ids)
    print(f"   Assigned {len(assigned_ids)} heading IDs:")
    for id_val in assigned_ids:
        print(f"     - {id_val}")
    print()
    
    # Test 3: Heading ladder validation
    print("🔧 TEST 3: Heading Ladder Validation")
    is_valid = processor.validate_heading_ladder(content_with_ids)
    print(f"   Heading ladder valid: {is_valid}")
    print()
    
    # Test 4: Mini-TOC building
    print("🔧 TEST 4: Mini-TOC Building")
    content_with_toc = processor.build_minitoc(content_with_ids)
    
    # Check for TOC elements
    has_minitoc = 'class="mini-toc"' in content_with_toc
    toc_links = content_with_toc.count('class="toc-link"')
    print(f"   Mini-TOC created: {has_minitoc}")
    print(f"   TOC links count: {toc_links}")
    print()
    
    # Test 5: Anchor resolution
    print("🔧 TEST 5: Anchor Resolution")
    anchors_resolve = processor.anchors_resolve(content_with_toc)
    print(f"   All anchors resolve: {anchors_resolve}")
    print()
    
    # Test 6: Complete pipeline
    print("🔧 TEST 6: Complete TICKET 2 Pipeline")
    result = processor._apply_stable_anchors_and_minitoc(test_content, "Test Article")
    
    print(f"   Pipeline success: {result.get('anchors_resolve', False)}")
    print(f"   Heading ladder valid: {result.get('heading_ladder_valid', False)}")
    print(f"   Changes applied: {len(result.get('changes_applied', []))}")
    
    for change in result.get('changes_applied', []):
        print(f"     - {change}")
    print()
    
    # Show final content sample
    print("🔧 FINAL CONTENT SAMPLE:")
    final_content = result.get('content', '')
    lines = final_content.split('\n')[:15]
    for line in lines:
        if line.strip():
            print(f"   {line}")
    
    print()
    print("✅ TICKET 2 DIRECT TESTING COMPLETE")
    
    # Summary
    success_indicators = [
        len(assigned_ids) > 0,
        has_minitoc,
        toc_links > 0,
        anchors_resolve,
        result.get('anchors_resolve', False)
    ]
    
    success_rate = sum(success_indicators) / len(success_indicators)
    print(f"📊 Success Rate: {success_rate:.1%} ({sum(success_indicators)}/{len(success_indicators)})")
    
    if success_rate >= 0.8:
        print("🎉 TICKET 2 implementation is working correctly!")
    elif success_rate >= 0.6:
        print("⚠️  TICKET 2 implementation is partially working.")
    else:
        print("❌ TICKET 2 implementation has issues.")

except Exception as e:
    print(f"❌ Error during testing: {e}")
    import traceback
    traceback.print_exc()