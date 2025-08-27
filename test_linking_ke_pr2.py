#!/usr/bin/env python3
"""
KE-PR2 Tests: Verify extracted TICKET 2/3 linking functionality
Tests for deterministic anchor IDs, TOC structure, and link building
"""

import sys
import os

# Add app root to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_anchor_generation():
    """Test deterministic anchor ID generation"""
    print("🧪 Testing anchor generation...")
    
    try:
        from engine.linking.anchors import stable_slug, anchor_id
        
        # Test stable_slug deterministic generation
        test_cases = [
            ("Getting Started Guide", "getting-started-guide"),
            ("API Reference & Examples", "api-reference-examples"),
            ("Multi-Word Heading With Spaces", "multi-word-heading-with-spaces"),
            ("Special Characters! @#$%", "special-characters"),
            ("Unicode: Café & Résumé", "unicode-cafe-resume"),
            ("", "section"),  # Empty fallback
        ]
        
        for input_text, expected in test_cases:
            result = stable_slug(input_text)
            if result == expected:
                print(f"  ✅ '{input_text}' -> '{result}'")
            else:
                print(f"  ❌ '{input_text}' -> '{result}' (expected '{expected}')")
                return False
        
        # Test anchor_id with prefix
        result = anchor_id("Getting Started", "intro")
        expected = "intro-getting-started"
        if result == expected:
            print(f"  ✅ Prefix test: '{result}'")
        else:
            print(f"  ❌ Prefix test: '{result}' (expected '{expected}')")
            return False
        
        print("✅ Anchor generation tests passed")
        return True
        
    except Exception as e:
        print(f"❌ Anchor generation test failed: {e}")
        return False


def test_heading_id_assignment():
    """Test heading ID assignment with HTML"""
    print("🧪 Testing heading ID assignment...")
    
    try:
        from engine.linking.anchors import assign_heading_ids
        
        test_html = """
        <div>
            <h2>Getting Started</h2>
            <p>Some content</p>
            <h3>Installation</h3>
            <p>More content</p>
            <h2>Getting Started</h2>
            <h4>Advanced Configuration</h4>
        </div>
        """
        
        result = assign_heading_ids(test_html)
        
        # Check that IDs are assigned
        expected_patterns = [
            'id="getting-started"',
            'id="installation"', 
            'id="getting-started-2"',  # Duplicate handling
            'id="advanced-configuration"'
        ]
        
        for pattern in expected_patterns:
            if pattern in result:
                print(f"  ✅ Found: {pattern}")
            else:
                print(f"  ❌ Missing: {pattern}")
                return False
        
        print("✅ Heading ID assignment tests passed")
        return True
        
    except Exception as e:
        print(f"❌ Heading ID assignment test failed: {e}")
        return False


def test_minitoc_generation():
    """Test Mini-TOC generation"""
    print("🧪 Testing Mini-TOC generation...")
    
    try:
        from engine.linking.toc import build_minitoc
        
        test_html = """
        <div>
            <p>Introduction paragraph</p>
            <h2 id="getting-started">Getting Started</h2>
            <p>Content here</p>
            <h3 id="installation">Installation</h3>
            <p>More content</p>
            <h2 id="api-reference">API Reference</h2>
            <p>API docs</p>
        </div>
        """
        
        result = build_minitoc(test_html)
        
        # Check Mini-TOC structure
        expected_patterns = [
            'class="mini-toc"',
            'class="toc-link"',
            'href="#getting-started"',
            'href="#installation"',
            'href="#api-reference"',
            'class="toc-l2"',  # H2 level
            'class="toc-l3"'   # H3 level
        ]
        
        for pattern in expected_patterns:
            if pattern in result:
                print(f"  ✅ Found TOC pattern: {pattern}")
            else:
                print(f"  ❌ Missing TOC pattern: {pattern}")
                return False
        
        print("✅ Mini-TOC generation tests passed")
        return True
        
    except Exception as e:
        print(f"❌ Mini-TOC generation test failed: {e}")
        return False


def test_anchor_resolution():
    """Test anchor link validation"""
    print("🧪 Testing anchor resolution...")
    
    try:
        from engine.linking.toc import anchors_resolve
        
        # Valid HTML with matching TOC and headings
        valid_html = """
        <div class="mini-toc">
            <ul>
                <li><a class="toc-link" href="#section-1">Section 1</a></li>
                <li><a class="toc-link" href="#section-2">Section 2</a></li>
            </ul>
        </div>
        <h2 id="section-1">Section 1</h2>
        <h2 id="section-2">Section 2</h2>
        """
        
        # Invalid HTML with broken links
        invalid_html = """
        <div class="mini-toc">
            <ul>
                <li><a class="toc-link" href="#missing-section">Missing Section</a></li>
            </ul>
        </div>
        <h2 id="existing-section">Existing Section</h2>
        """
        
        valid_result = anchors_resolve(valid_html)
        invalid_result = anchors_resolve(invalid_html)
        
        if valid_result and not invalid_result:
            print("  ✅ Anchor resolution correctly identifies valid/invalid links")
        else:
            print(f"  ❌ Anchor resolution failed: valid={valid_result}, invalid={invalid_result}")
            return False
        
        print("✅ Anchor resolution tests passed")
        return True
        
    except Exception as e:
        print(f"❌ Anchor resolution test failed: {e}")
        return False


def test_bookmark_generation():
    """Test bookmark registry extraction"""
    print("🧪 Testing bookmark generation...")
    
    try:
        from engine.linking.bookmarks import extract_headings_registry, generate_doc_uid, generate_doc_slug
        
        # Test heading extraction
        test_html = """
        <h2 id="intro">Introduction</h2>
        <h3 id="overview">Overview</h3>
        <h2 id="api">API Reference</h2>
        <h4 id="methods">Methods</h4>
        """
        
        headings = extract_headings_registry(test_html)
        
        if len(headings) == 4:
            print(f"  ✅ Extracted {len(headings)} headings")
        else:
            print(f"  ❌ Expected 4 headings, got {len(headings)}")
            return False
        
        # Check heading structure
        expected_ids = ["intro", "overview", "api", "methods"]
        for i, heading in enumerate(headings):
            if heading["id"] == expected_ids[i] and "text" in heading and "level" in heading:
                print(f"  ✅ Heading {i+1}: {heading['id']}")
            else:
                print(f"  ❌ Invalid heading structure: {heading}")
                return False
        
        # Test UID generation (should be deterministic format)
        uid = generate_doc_uid()
        if uid.startswith("01JZ") and len(uid) == 20:
            print(f"  ✅ Generated valid doc_uid: {uid}")
        else:
            print(f"  ❌ Invalid doc_uid format: {uid}")
            return False
        
        # Test slug generation
        slug = generate_doc_slug("My Test Document & Guide")
        expected_slug = "my-test-document-guide"
        if slug == expected_slug:
            print(f"  ✅ Generated doc_slug: {slug}")
        else:
            print(f"  ❌ Doc_slug mismatch: {slug} != {expected_slug}")
            return False
        
        print("✅ Bookmark generation tests passed")
        return True
        
    except Exception as e:
        print(f"❌ Bookmark generation test failed: {e}")
        return False


def test_link_building():
    """Test environment-aware link building"""
    print("🧪 Testing link building...")
    
    try:
        from engine.linking.links import build_href, get_default_route_map, build_link
        
        # Test simple link building
        link = build_link("my-document", "section-1", "https://example.com")
        expected = "https://example.com/docs/my-document#section-1"
        if link == expected:
            print(f"  ✅ Simple link: {link}")
        else:
            print(f"  ❌ Simple link mismatch: {link} != {expected}")
            return False
        
        # Test route map
        route_map = get_default_route_map("content_library")
        if "routes" in route_map and "prefer" in route_map:
            print(f"  ✅ Route map structure valid")
        else:
            print(f"  ❌ Invalid route map: {route_map}")
            return False
        
        # Test href building
        target_doc = {
            "doc_uid": "test-uid-123",
            "doc_slug": "test-document",
            "title": "Test Document"
        }
        
        href = build_href(target_doc, "intro", route_map)
        # Should contain the document reference and anchor
        if "#intro" in href and ("test-document" in href or "test-uid-123" in href):
            print(f"  ✅ Environment href: {href}")
        else:
            print(f"  ❌ Invalid href: {href}")
            return False
        
        print("✅ Link building tests passed")
        return True
        
    except Exception as e:
        print(f"❌ Link building test failed: {e}")
        return False


def test_integration():
    """Test full integration: IDs -> TOC -> Links"""
    print("🧪 Testing full integration...")
    
    try:
        from engine.linking.anchors import assign_heading_ids
        from engine.linking.toc import build_minitoc, anchors_resolve
        from engine.linking.bookmarks import extract_headings_registry
        
        # Start with raw HTML
        raw_html = """
        <div>
            <p>Welcome to our guide</p>
            <h2>Getting Started</h2>
            <p>Let's begin</p>
            <h3>Installation</h3>
            <p>Install the software</p>
            <h2>Advanced Usage</h2>
            <p>Advanced topics</p>
        </div>
        """
        
        # Step 1: Assign IDs
        html_with_ids = assign_heading_ids(raw_html)
        
        # Step 2: Build Mini-TOC
        html_with_toc = build_minitoc(html_with_ids)
        
        # Step 3: Validate anchors resolve
        anchors_valid = anchors_resolve(html_with_toc)
        
        # Step 4: Extract bookmark registry
        headings = extract_headings_registry(html_with_toc)
        
        # Verify integration
        if not anchors_valid:
            print("  ❌ Anchors don't resolve after full processing")
            return False
        
        if len(headings) < 3:  # Should have 3 headings
            print(f"  ❌ Expected 3+ headings in registry, got {len(headings)}")
            return False
        
        # Check for expected patterns in final HTML
        expected_patterns = [
            'class="mini-toc"',       # TOC container
            'class="toc-link"',       # TOC links
            'id="getting-started"',   # Assigned IDs
            'href="#getting-started"' # Matching hrefs
        ]
        
        for pattern in expected_patterns:
            if pattern not in html_with_toc:
                print(f"  ❌ Missing integration pattern: {pattern}")
                return False
        
        print("  ✅ Full pipeline: Raw HTML -> IDs -> TOC -> Validation -> Registry")
        print("✅ Integration tests passed")
        return True
        
    except Exception as e:
        print(f"❌ Integration test failed: {e}")
        return False


if __name__ == "__main__":
    print("🧪 Running KE-PR2 TICKET 2/3 Linking Tests...")
    print("=" * 60)
    
    tests = [
        test_anchor_generation,
        test_heading_id_assignment,
        test_minitoc_generation,
        test_anchor_resolution,
        test_bookmark_generation,
        test_link_building,
        test_integration
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
    
    print("=" * 60)
    print(f"📊 Test Results: {passed}/{len(tests)} tests passed")
    
    if passed == len(tests):
        print("🎉 KE-PR2 linking extraction is working correctly!")
        print("✅ All TICKET 2/3 functionality preserved")
        exit(0)
    else:
        print("❌ KE-PR2 linking extraction has issues")
        exit(1)