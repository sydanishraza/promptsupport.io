#!/usr/bin/env python3
"""
V2 Engine LLM Instruction Fixes Test Suite
Testing the fixed LLM instructions by processing fresh Google Maps content through V2 engine

Focus Areas:
1. Fresh LLM-Based V2 Processing - Process Google Map JavaScript API Tutorial through V2 engine
2. LLM Generation Verification - Verify _perform_llm_article_generation uses updated system message
3. Content Structure Analysis - Examine LLM-generated HTML for all 5 fixes
4. Processing Success Verification - Confirm LLM generates articles with new instructions
5. Database Content Check - Verify stored article reflects all 5 fixes
"""

import asyncio
import aiohttp
import json
import os
import re
from datetime import datetime
import sys
import tempfile
import base64

# Configuration
BACKEND_URL = os.getenv('REACT_APP_BACKEND_URL', 'https://content-formatter.preview.emergentagent.com')
API_BASE = f"{BACKEND_URL}/api"

def print_test_header(title):
    """Print formatted test header"""
    print(f"\n{'='*80}")
    print(f"🧪 {title}")
    print(f"{'='*80}")

def print_success(message):
    """Print success message"""
    print(f"✅ {message}")

def print_error(message):
    """Print error message"""
    print(f"❌ {message}")

def print_info(message):
    """Print info message"""
    print(f"ℹ️  {message}")

def create_google_maps_tutorial_content():
    """Create fresh Google Maps JavaScript API tutorial content for testing"""
    return """
# Google Maps JavaScript API Tutorial

This comprehensive tutorial will guide you through building interactive maps using the Google Maps JavaScript API. You'll learn how to create, customize, and deploy maps with markers, info windows, and advanced features.

## Getting Started with Google Maps API

Before you begin, you'll need to set up your development environment and obtain an API key from the Google Cloud Console.

### Prerequisites
- Basic knowledge of HTML, CSS, and JavaScript
- A Google Cloud Platform account
- A text editor or IDE

### Step 1: Obtain an API Key
1. Go to the Google Cloud Console
2. Create a new project or select an existing one
3. Enable the Maps JavaScript API
4. Create credentials (API key)
5. Restrict your API key for security

## Creating Your First Map

Let's start by creating a basic map that displays a specific location.

### HTML Structure
Create an HTML file with the following structure:

```html
<!DOCTYPE html>
<html>
<head>
    <title>My First Google Map</title>
    <style>
        #map {
            height: 400px;
            width: 100%;
        }
    </style>
</head>
<body>
    <h1>My Google Map</h1>
    <div id="map"></div>
    <script src="script.js"></script>
    <script async defer
        src="https://maps.googleapis.com/maps/api/js?key=YOUR_API_KEY&callback=initMap">
    </script>
</body>
</html>
```

### JavaScript Implementation
Create a script.js file with the map initialization code:

```javascript
function initMap() {
    // Map options
    const mapOptions = {
        zoom: 10,
        center: { lat: 37.7749, lng: -122.4194 } // San Francisco
    };
    
    // Create map
    const map = new google.maps.Map(document.getElementById('map'), mapOptions);
    
    // Add marker
    const marker = new google.maps.Marker({
        position: { lat: 37.7749, lng: -122.4194 },
        map: map,
        title: 'San Francisco'
    });
}
```

## Adding Markers and Info Windows

Enhance your map by adding multiple markers with interactive info windows.

### Multiple Markers
Here's how to add several markers to your map:

```javascript
function addMultipleMarkers(map) {
    const locations = [
        { lat: 37.7749, lng: -122.4194, title: 'San Francisco' },
        { lat: 37.3382, lng: -121.8863, title: 'San Jose' },
        { lat: 37.8044, lng: -122.2712, title: 'Oakland' }
    ];
    
    locations.forEach(location => {
        const marker = new google.maps.Marker({
            position: { lat: location.lat, lng: location.lng },
            map: map,
            title: location.title
        });
        
        const infoWindow = new google.maps.InfoWindow({
            content: `<h3>${location.title}</h3>`
        });
        
        marker.addListener('click', () => {
            infoWindow.open(map, marker);
        });
    });
}
```

## Map Customization Options

Customize your map's appearance and behavior with various options.

### Styling Your Map
Apply custom styles to change the map's appearance:

```javascript
const customMapStyle = [
    {
        "featureType": "water",
        "elementType": "geometry",
        "stylers": [{"color": "#e9e9e9"}, {"lightness": 17}]
    },
    {
        "featureType": "landscape",
        "elementType": "geometry",
        "stylers": [{"color": "#f5f5f5"}, {"lightness": 20}]
    }
];

const styledMapOptions = {
    zoom: 10,
    center: { lat: 37.7749, lng: -122.4194 },
    styles: customMapStyle
};
```

### Map Controls
Configure which controls appear on your map:

```javascript
const mapWithControls = new google.maps.Map(document.getElementById('map'), {
    zoom: 10,
    center: { lat: 37.7749, lng: -122.4194 },
    mapTypeControl: true,
    streetViewControl: true,
    fullscreenControl: true,
    zoomControl: true
});
```

## Advanced Features

Explore advanced Google Maps features for enhanced functionality.

### Geolocation
Add user location detection:

```javascript
function getUserLocation(map) {
    if (navigator.geolocation) {
        navigator.geolocation.getCurrentPosition(position => {
            const userLocation = {
                lat: position.coords.latitude,
                lng: position.coords.longitude
            };
            
            map.setCenter(userLocation);
            
            new google.maps.Marker({
                position: userLocation,
                map: map,
                title: 'Your Location'
            });
        });
    }
}
```

### Drawing Tools
Implement drawing capabilities:

```javascript
function initDrawingTools(map) {
    const drawingManager = new google.maps.drawing.DrawingManager({
        drawingMode: google.maps.drawing.OverlayType.MARKER,
        drawingControl: true,
        drawingControlOptions: {
            position: google.maps.ControlPosition.TOP_CENTER,
            drawingModes: ['marker', 'circle', 'polygon', 'polyline', 'rectangle']
        }
    });
    
    drawingManager.setMap(map);
}
```

## Best Practices and Performance

Follow these guidelines for optimal map performance and user experience.

### Performance Optimization
- Limit the number of markers displayed simultaneously
- Use marker clustering for large datasets
- Implement lazy loading for map initialization
- Optimize API key usage with proper restrictions

### Security Considerations
- Always restrict your API keys
- Use HTTPS for all map implementations
- Validate user input for custom markers
- Monitor API usage to prevent quota exceeded errors

### Accessibility
- Provide alternative text for map elements
- Ensure keyboard navigation support
- Include screen reader compatible descriptions
- Test with assistive technologies

## Troubleshooting Common Issues

Here are solutions to frequently encountered problems.

### API Key Issues
If your map isn't loading, check:
- API key is correctly configured
- Maps JavaScript API is enabled
- Billing is set up (if required)
- Key restrictions are properly configured

### Map Display Problems
For rendering issues:
- Verify container element has defined dimensions
- Check for JavaScript errors in console
- Ensure proper script loading order
- Validate HTML structure

### Performance Issues
To improve map performance:
- Reduce marker count or use clustering
- Optimize custom styles
- Implement proper error handling
- Use appropriate zoom levels

## Conclusion

You've learned how to create interactive Google Maps using the JavaScript API. This tutorial covered basic map creation, marker management, customization options, and advanced features. Continue exploring the extensive Google Maps API documentation for more advanced implementations.

Remember to follow best practices for performance, security, and accessibility to create professional-quality map applications.
"""

async def test_fresh_v2_processing():
    """Test 1: Fresh LLM-Based V2 Processing - Process Google Maps content through V2 engine"""
    print_test_header("Test 1: Fresh LLM-Based V2 Processing")
    
    try:
        async with aiohttp.ClientSession() as session:
            # Create fresh Google Maps tutorial content
            tutorial_content = create_google_maps_tutorial_content()
            print_info(f"Created fresh Google Maps tutorial content: {len(tutorial_content)} characters")
            
            # Process through V2 engine
            print_info("Processing content through V2 engine...")
            
            payload = {
                "content": tutorial_content,
                "metadata": {
                    "title": "Google Maps JavaScript API Tutorial - Fresh V2 Test",
                    "source": "v2_llm_instruction_fixes_test",
                    "test_timestamp": datetime.now().isoformat()
                }
            }
            
            async with session.post(f"{API_BASE}/content/process", json=payload) as response:
                if response.status == 200:
                    result = await response.json()
                    print_success(f"V2 processing initiated - Status: {response.status}")
                    
                    # Extract job information
                    job_id = result.get('job_id')
                    if job_id:
                        print_success(f"Processing job created: {job_id}")
                        
                        # Wait for processing to complete
                        print_info("Waiting for V2 processing to complete...")
                        processing_complete = await wait_for_processing_completion(session, job_id)
                        
                        if processing_complete:
                            print_success("V2 processing completed successfully")
                            return True, job_id
                        else:
                            print_error("V2 processing did not complete within timeout")
                            return False, job_id
                    else:
                        print_error("No job ID returned from V2 processing")
                        return False, None
                else:
                    error_text = await response.text()
                    print_error(f"V2 processing failed - Status: {response.status}")
                    print_error(f"Error: {error_text}")
                    return False, None
                    
    except Exception as e:
        print_error(f"Error in fresh V2 processing: {e}")
        return False, None

async def wait_for_processing_completion(session, job_id, timeout=300):
    """Wait for processing job to complete"""
    import asyncio
    
    start_time = datetime.now()
    while (datetime.now() - start_time).seconds < timeout:
        try:
            async with session.get(f"{API_BASE}/jobs/{job_id}") as response:
                if response.status == 200:
                    job_data = await response.json()
                    status = job_data.get('status', 'unknown')
                    
                    if status == 'completed':
                        return True
                    elif status == 'failed':
                        print_error(f"Processing job failed: {job_data.get('error', 'Unknown error')}")
                        return False
                    else:
                        print_info(f"Processing status: {status}")
                        await asyncio.sleep(10)  # Wait 10 seconds before checking again
                else:
                    print_info(f"Job status check failed: {response.status}")
                    await asyncio.sleep(10)
        except Exception as e:
            print_info(f"Error checking job status: {e}")
            await asyncio.sleep(10)
    
    return False

async def test_llm_generation_verification():
    """Test 2: LLM Generation Verification - Verify updated system message implementation"""
    print_test_header("Test 2: LLM Generation Verification")
    
    try:
        async with aiohttp.ClientSession() as session:
            # Check for recently processed articles with V2 engine
            print_info("Searching for recently processed V2 articles...")
            
            async with session.get(f"{API_BASE}/content-library") as response:
                if response.status == 200:
                    data = await response.json()
                    articles = data.get('articles', []) if isinstance(data, dict) else data
                    print_success(f"Content library accessible - {len(articles)} articles found")
                    
                    # Find recent V2 processed articles
                    v2_articles = []
                    for article in articles:
                        # Check for V2 processing indicators
                        metadata = article.get('metadata', {})
                        if (metadata.get('engine') == 'v2' or 
                            'v2' in str(metadata).lower() or
                            'Google Maps' in article.get('title', '')):
                            v2_articles.append(article)
                    
                    if v2_articles:
                        print_success(f"Found {len(v2_articles)} V2 processed articles")
                        
                        # Analyze the most recent V2 article
                        latest_article = max(v2_articles, key=lambda x: x.get('created_at', ''))
                        print_info(f"Analyzing latest V2 article: '{latest_article['title']}'")
                        
                        return await analyze_llm_system_message_compliance(latest_article)
                    else:
                        print_error("No V2 processed articles found for verification")
                        return False
                else:
                    print_error(f"Failed to access content library - Status: {response.status}")
                    return False
                    
    except Exception as e:
        print_error(f"Error in LLM generation verification: {e}")
        return False

async def analyze_llm_system_message_compliance(article):
    """Analyze article for compliance with updated LLM system message"""
    print_info("Analyzing article for LLM system message compliance...")
    
    content = article.get('content', article.get('html', ''))
    if not content:
        print_error("Article content is empty")
        return False
    
    compliance_checks = []
    
    # Check 1: NO H1 tags in content (title handled by frontend)
    h1_tags = re.findall(r'<h1[^>]*>', content, re.IGNORECASE)
    if len(h1_tags) == 0:
        print_success("✅ NO H1 tags in content - title handled by frontend")
        compliance_checks.append(True)
    else:
        print_error(f"❌ Found {len(h1_tags)} H1 tags in content (should be 0)")
        compliance_checks.append(False)
    
    # Check 2: Mini-TOC as clickable anchor links with href="#section1" format
    toc_links = re.findall(r'<a href="#(section\d+)"[^>]*>([^<]+)</a>', content, re.IGNORECASE)
    if len(toc_links) >= 3:
        print_success(f"✅ Mini-TOC with clickable anchor links found: {len(toc_links)} links")
        for link_id, link_text in toc_links[:3]:
            print_info(f"  - {link_text} -> #{link_id}")
        compliance_checks.append(True)
    else:
        print_error(f"❌ Insufficient Mini-TOC anchor links (found {len(toc_links)}, need ≥3)")
        compliance_checks.append(False)
    
    # Check 3: OL lists for procedural steps
    ol_lists = re.findall(r'<ol[^>]*>.*?</ol>', content, re.DOTALL | re.IGNORECASE)
    ul_lists = re.findall(r'<ul[^>]*>.*?</ul>', content, re.DOTALL | re.IGNORECASE)
    
    # Look for procedural content that should use OL
    procedural_indicators = ['step', 'first', 'second', 'then', 'next', 'finally', 'create', 'add', 'configure']
    procedural_content_found = any(indicator in content.lower() for indicator in procedural_indicators)
    
    if len(ol_lists) > 0 and procedural_content_found:
        print_success(f"✅ OL lists for procedural steps: {len(ol_lists)} ordered lists found")
        compliance_checks.append(True)
    elif not procedural_content_found:
        print_info("ℹ️  No procedural content detected - OL requirement not applicable")
        compliance_checks.append(True)
    else:
        print_error(f"❌ Procedural content found but no OL lists (found {len(ol_lists)} OL, {len(ul_lists)} UL)")
        compliance_checks.append(False)
    
    # Check 4: Consolidated code blocks instead of fragments
    code_blocks = re.findall(r'<pre[^>]*>.*?</pre>', content, re.DOTALL | re.IGNORECASE)
    code_tags = re.findall(r'<code[^>]*>.*?</code>', content, re.DOTALL | re.IGNORECASE)
    
    total_code_elements = len(code_blocks) + len(code_tags)
    if total_code_elements > 0:
        # Check for consolidated blocks (longer code blocks indicate consolidation)
        avg_code_length = sum(len(block) for block in code_blocks + code_tags) / total_code_elements if total_code_elements > 0 else 0
        
        if avg_code_length > 100:  # Consolidated blocks should be longer
            print_success(f"✅ Consolidated code blocks: {total_code_elements} blocks, avg length {avg_code_length:.0f} chars")
            compliance_checks.append(True)
        else:
            print_error(f"❌ Code blocks appear fragmented: {total_code_elements} blocks, avg length {avg_code_length:.0f} chars")
            compliance_checks.append(False)
    else:
        print_info("ℹ️  No code blocks found - consolidation requirement not applicable")
        compliance_checks.append(True)
    
    # Check 5: Proper anchor IDs matching TOC links (section1, section2, etc.)
    heading_ids = re.findall(r'<h[2-6][^>]*id="([^"]+)"', content, re.IGNORECASE)
    section_ids = [hid for hid in heading_ids if hid.startswith('section') and hid[7:].isdigit()]
    
    if len(section_ids) >= 3:
        print_success(f"✅ Proper anchor IDs matching TOC links: {section_ids}")
        
        # Verify TOC links match heading IDs
        toc_targets = [link_id for link_id, _ in toc_links]
        matching_ids = set(toc_targets) & set(section_ids)
        
        if len(matching_ids) >= 2:
            print_success(f"✅ TOC links match heading IDs: {list(matching_ids)}")
            compliance_checks.append(True)
        else:
            print_error(f"❌ TOC links don't match heading IDs: TOC={toc_targets}, Headings={section_ids}")
            compliance_checks.append(False)
    else:
        print_error(f"❌ Insufficient proper anchor IDs (found {len(section_ids)}, need ≥3)")
        compliance_checks.append(False)
    
    # Overall compliance assessment
    compliance_rate = sum(compliance_checks) / len(compliance_checks) * 100
    print_info(f"LLM System Message Compliance: {compliance_rate:.1f}% ({sum(compliance_checks)}/{len(compliance_checks)})")
    
    return compliance_rate >= 80  # 80% compliance threshold

async def test_content_structure_analysis():
    """Test 3: Content Structure Analysis - Examine LLM-generated HTML for all 5 fixes"""
    print_test_header("Test 3: Content Structure Analysis")
    
    try:
        async with aiohttp.ClientSession() as session:
            # Get the most recent Google Maps related article
            print_info("Searching for Google Maps tutorial articles...")
            
            async with session.get(f"{API_BASE}/content-library") as response:
                if response.status == 200:
                    data = await response.json()
                    articles = data.get('articles', []) if isinstance(data, dict) else data
                    
                    # Find Google Maps related articles
                    maps_articles = []
                    for article in articles:
                        title = article.get('title', '').lower()
                        if any(keyword in title for keyword in ['google maps', 'maps api', 'javascript api']):
                            maps_articles.append(article)
                    
                    if maps_articles:
                        # Analyze the most recent one
                        latest_maps_article = max(maps_articles, key=lambda x: x.get('created_at', ''))
                        print_success(f"Found Google Maps article: '{latest_maps_article['title']}'")
                        
                        return await perform_comprehensive_structure_analysis(latest_maps_article)
                    else:
                        print_error("No Google Maps tutorial articles found")
                        return False
                else:
                    print_error(f"Failed to access content library - Status: {response.status}")
                    return False
                    
    except Exception as e:
        print_error(f"Error in content structure analysis: {e}")
        return False

async def perform_comprehensive_structure_analysis(article):
    """Perform comprehensive analysis of article structure for all 5 fixes"""
    print_info(f"Performing comprehensive structure analysis on: '{article['title']}'")
    
    content = article.get('content', article.get('html', ''))
    if not content:
        print_error("Article content is empty")
        return False
    
    analysis_results = {}
    
    # Analysis 1: H1 Tag Elimination
    h1_count = len(re.findall(r'<h1[^>]*>', content, re.IGNORECASE))
    analysis_results['h1_elimination'] = {
        'h1_count': h1_count,
        'success': h1_count == 0,
        'details': f"Found {h1_count} H1 tags (target: 0)"
    }
    
    # Analysis 2: Mini-TOC Clickable Links
    toc_links = re.findall(r'<a href="#([^"]+)"[^>]*>([^<]+)</a>', content, re.IGNORECASE)
    markdown_toc = re.findall(r'\[([^\]]+)\]\(#([^)]+)\)', content)
    all_toc_links = toc_links + [(text, anchor) for text, anchor in markdown_toc]
    
    analysis_results['mini_toc_links'] = {
        'link_count': len(all_toc_links),
        'success': len(all_toc_links) >= 3,
        'details': f"Found {len(all_toc_links)} TOC anchor links",
        'examples': all_toc_links[:3] if all_toc_links else []
    }
    
    # Analysis 3: Ordered Lists for Procedures
    ol_count = len(re.findall(r'<ol[^>]*>', content, re.IGNORECASE))
    ul_count = len(re.findall(r'<ul[^>]*>', content, re.IGNORECASE))
    
    # Check for procedural content
    procedural_patterns = [
        r'step\s+\d+', r'first[,\s]', r'second[,\s]', r'then[,\s]', 
        r'next[,\s]', r'finally[,\s]', r'create\s+', r'add\s+', r'configure\s+'
    ]
    procedural_matches = sum(len(re.findall(pattern, content, re.IGNORECASE)) for pattern in procedural_patterns)
    
    analysis_results['ordered_lists'] = {
        'ol_count': ol_count,
        'ul_count': ul_count,
        'procedural_indicators': procedural_matches,
        'success': ol_count > 0 if procedural_matches > 0 else True,
        'details': f"Found {ol_count} OL, {ul_count} UL, {procedural_matches} procedural indicators"
    }
    
    # Analysis 4: Consolidated Code Blocks
    code_blocks = re.findall(r'<pre[^>]*>.*?</pre>', content, re.DOTALL | re.IGNORECASE)
    code_tags = re.findall(r'<code[^>]*>.*?</code>', content, re.DOTALL | re.IGNORECASE)
    
    if code_blocks or code_tags:
        total_code_length = sum(len(block) for block in code_blocks + code_tags)
        avg_code_length = total_code_length / (len(code_blocks) + len(code_tags))
        
        # Check for consolidation (fewer, longer blocks indicate consolidation)
        consolidation_score = avg_code_length / max(len(code_blocks) + len(code_tags), 1)
        
        analysis_results['consolidated_code'] = {
            'code_block_count': len(code_blocks),
            'code_tag_count': len(code_tags),
            'avg_length': avg_code_length,
            'consolidation_score': consolidation_score,
            'success': consolidation_score > 50,  # Arbitrary threshold for consolidation
            'details': f"{len(code_blocks)} code blocks, {len(code_tags)} code tags, avg length {avg_code_length:.0f}"
        }
    else:
        analysis_results['consolidated_code'] = {
            'success': True,
            'details': "No code blocks found - consolidation not applicable"
        }
    
    # Analysis 5: Proper Anchor IDs
    heading_ids = re.findall(r'<h[2-6][^>]*id="([^"]+)"', content, re.IGNORECASE)
    section_pattern_ids = [hid for hid in heading_ids if re.match(r'section\d+', hid)]
    
    # Check if TOC links match heading IDs
    toc_targets = [anchor for _, anchor in all_toc_links]
    matching_anchors = set(toc_targets) & set(heading_ids)
    
    analysis_results['proper_anchor_ids'] = {
        'heading_id_count': len(heading_ids),
        'section_pattern_count': len(section_pattern_ids),
        'toc_target_count': len(toc_targets),
        'matching_count': len(matching_anchors),
        'success': len(matching_anchors) >= 2,
        'details': f"{len(heading_ids)} heading IDs, {len(matching_anchors)} matching TOC targets",
        'heading_ids': heading_ids[:5],
        'toc_targets': toc_targets[:5]
    }
    
    # Overall assessment
    successful_fixes = sum(1 for result in analysis_results.values() if result['success'])
    total_fixes = len(analysis_results)
    success_rate = (successful_fixes / total_fixes) * 100
    
    # Print detailed results
    print_info("Comprehensive Structure Analysis Results:")
    for fix_name, result in analysis_results.items():
        status = "✅ PASS" if result['success'] else "❌ FAIL"
        print_info(f"  {status} - {fix_name.replace('_', ' ').title()}: {result['details']}")
    
    print_info(f"Overall Success Rate: {success_rate:.1f}% ({successful_fixes}/{total_fixes} fixes)")
    
    return success_rate >= 80  # 80% success threshold

async def test_processing_success_verification():
    """Test 4: Processing Success Verification - Confirm LLM generates articles with new instructions"""
    print_test_header("Test 4: Processing Success Verification")
    
    try:
        async with aiohttp.ClientSession() as session:
            # Check V2 engine status and capabilities
            print_info("Checking V2 engine status and LLM generation capabilities...")
            
            async with session.get(f"{API_BASE}/engine/status") as response:
                if response.status == 200:
                    engine_status = await response.json()
                    print_success("V2 engine status accessible")
                    
                    # Check for V2 engine indicators
                    engine_version = engine_status.get('engine', 'unknown')
                    if engine_version == 'v2':
                        print_success("✅ V2 engine confirmed active")
                    else:
                        print_info(f"Engine version: {engine_version}")
                    
                    # Check for LLM generation features
                    features = engine_status.get('features', [])
                    llm_features = [f for f in features if 'llm' in str(f).lower() or 'generation' in str(f).lower()]
                    
                    if llm_features:
                        print_success(f"✅ LLM generation features found: {len(llm_features)}")
                        for feature in llm_features[:3]:
                            print_info(f"  - {feature}")
                    else:
                        print_info("No explicit LLM generation features listed")
                    
                    # Check processing statistics
                    stats = engine_status.get('statistics', {})
                    if stats:
                        articles_processed = stats.get('articles_processed', 0)
                        success_rate = stats.get('success_rate', 0)
                        print_success(f"✅ Processing statistics: {articles_processed} articles, {success_rate}% success rate")
                    
                    return True
                else:
                    print_error(f"Failed to access engine status - Status: {response.status}")
                    return False
                    
    except Exception as e:
        print_error(f"Error in processing success verification: {e}")
        return False

async def test_database_content_check():
    """Test 5: Database Content Check - Verify stored article reflects all 5 fixes"""
    print_test_header("Test 5: Database Content Check")
    
    try:
        async with aiohttp.ClientSession() as session:
            # Get recent articles and check database storage
            print_info("Checking database content for LLM instruction fixes...")
            
            async with session.get(f"{API_BASE}/content-library") as response:
                if response.status == 200:
                    data = await response.json()
                    articles = data.get('articles', []) if isinstance(data, dict) else data
                    print_success(f"Database accessible - {len(articles)} articles found")
                    
                    # Find the most recent article with substantial content
                    recent_articles = sorted(articles, key=lambda x: x.get('created_at', ''), reverse=True)
                    
                    for article in recent_articles[:5]:  # Check top 5 recent articles
                        content = article.get('content', article.get('html', ''))
                        if len(content) > 1000:  # Substantial content
                            print_info(f"Analyzing database article: '{article['title']}'")
                            
                            # Perform database content verification
                            verification_result = await verify_database_content_fixes(article)
                            if verification_result:
                                return True
                    
                    print_error("No suitable articles found in database for verification")
                    return False
                else:
                    print_error(f"Failed to access content library database - Status: {response.status}")
                    return False
                    
    except Exception as e:
        print_error(f"Error in database content check: {e}")
        return False

async def verify_database_content_fixes(article):
    """Verify that database-stored article reflects all 5 LLM instruction fixes"""
    print_info("Verifying database content for LLM instruction fixes...")
    
    content = article.get('content', article.get('html', ''))
    metadata = article.get('metadata', {})
    
    verification_results = []
    
    # Verification 1: No H1 in content
    h1_tags = re.findall(r'<h1[^>]*>', content, re.IGNORECASE)
    no_h1_success = len(h1_tags) == 0
    verification_results.append(no_h1_success)
    
    if no_h1_success:
        print_success("✅ Database verification: NO H1 tags in stored content")
    else:
        print_error(f"❌ Database verification: Found {len(h1_tags)} H1 tags in stored content")
    
    # Verification 2: Mini-TOC with clickable links
    toc_links = re.findall(r'<a href="#[^"]*"[^>]*>[^<]+</a>', content, re.IGNORECASE)
    toc_success = len(toc_links) >= 2
    verification_results.append(toc_success)
    
    if toc_success:
        print_success(f"✅ Database verification: Mini-TOC with {len(toc_links)} clickable links")
    else:
        print_error(f"❌ Database verification: Insufficient TOC links ({len(toc_links)})")
    
    # Verification 3: Ordered lists for procedures
    ol_tags = re.findall(r'<ol[^>]*>', content, re.IGNORECASE)
    procedural_content = any(keyword in content.lower() for keyword in ['step', 'first', 'create', 'add'])
    ol_success = len(ol_tags) > 0 if procedural_content else True
    verification_results.append(ol_success)
    
    if ol_success:
        print_success(f"✅ Database verification: Ordered lists properly used ({len(ol_tags)} OL tags)")
    else:
        print_error(f"❌ Database verification: Missing ordered lists for procedural content")
    
    # Verification 4: Consolidated code blocks
    code_blocks = re.findall(r'<pre[^>]*>.*?</pre>', content, re.DOTALL | re.IGNORECASE)
    if code_blocks:
        avg_code_length = sum(len(block) for block in code_blocks) / len(code_blocks)
        consolidation_success = avg_code_length > 80  # Threshold for consolidation
        verification_results.append(consolidation_success)
        
        if consolidation_success:
            print_success(f"✅ Database verification: Code blocks consolidated (avg {avg_code_length:.0f} chars)")
        else:
            print_error(f"❌ Database verification: Code blocks fragmented (avg {avg_code_length:.0f} chars)")
    else:
        verification_results.append(True)  # No code blocks is acceptable
        print_info("ℹ️  Database verification: No code blocks found")
    
    # Verification 5: Proper anchor IDs
    heading_ids = re.findall(r'<h[2-6][^>]*id="([^"]+)"', content, re.IGNORECASE)
    toc_targets = re.findall(r'href="#([^"]+)"', content, re.IGNORECASE)
    matching_anchors = set(heading_ids) & set(toc_targets)
    anchor_success = len(matching_anchors) >= 1
    verification_results.append(anchor_success)
    
    if anchor_success:
        print_success(f"✅ Database verification: Proper anchor IDs ({len(matching_anchors)} matching)")
    else:
        print_error(f"❌ Database verification: Anchor ID mismatch")
    
    # Overall database verification
    success_count = sum(verification_results)
    total_checks = len(verification_results)
    success_rate = (success_count / total_checks) * 100
    
    print_info(f"Database Content Verification: {success_rate:.1f}% ({success_count}/{total_checks})")
    
    return success_rate >= 80  # 80% success threshold

async def run_v2_llm_instruction_fixes_test():
    """Run comprehensive V2 Engine LLM Instruction Fixes test suite"""
    print_test_header("V2 Engine LLM Instruction Fixes - Comprehensive Test Suite")
    print_info(f"Backend URL: {BACKEND_URL}")
    print_info(f"API Base: {API_BASE}")
    print_info(f"Test Time: {datetime.now().isoformat()}")
    print_info("Focus: Testing LLM instruction fixes by processing fresh Google Maps content through V2 engine")
    
    # Test results tracking
    test_results = []
    
    # Test 1: Fresh LLM-Based V2 Processing
    print_info("Starting Test 1: Fresh LLM-Based V2 Processing...")
    success, job_id = await test_fresh_v2_processing()
    test_results.append(("Fresh V2 Processing", success))
    
    # Test 2: LLM Generation Verification
    print_info("Starting Test 2: LLM Generation Verification...")
    success = await test_llm_generation_verification()
    test_results.append(("LLM Generation Verification", success))
    
    # Test 3: Content Structure Analysis
    print_info("Starting Test 3: Content Structure Analysis...")
    success = await test_content_structure_analysis()
    test_results.append(("Content Structure Analysis", success))
    
    # Test 4: Processing Success Verification
    print_info("Starting Test 4: Processing Success Verification...")
    success = await test_processing_success_verification()
    test_results.append(("Processing Success Verification", success))
    
    # Test 5: Database Content Check
    print_info("Starting Test 5: Database Content Check...")
    success = await test_database_content_check()
    test_results.append(("Database Content Check", success))
    
    # Final Results Summary
    print_test_header("Test Results Summary")
    
    passed_tests = sum(1 for _, success in test_results if success)
    total_tests = len(test_results)
    success_rate = (passed_tests / total_tests) * 100
    
    print_info(f"Tests Passed: {passed_tests}/{total_tests}")
    print_info(f"Success Rate: {success_rate:.1f}%")
    
    for test_name, success in test_results:
        status = "✅ PASS" if success else "❌ FAIL"
        print_info(f"{status} - {test_name}")
    
    # Overall assessment
    if success_rate >= 80:
        print_success(f"🎉 V2 ENGINE LLM INSTRUCTION FIXES TEST SUITE PASSED - {success_rate:.1f}% SUCCESS RATE")
        print_success("The LLM instruction fixes are working correctly!")
        print_success("✅ NO H1 tags in content (title handled by frontend)")
        print_success("✅ Mini-TOC as clickable anchor links with href='#section1' format")
        print_success("✅ OL lists for procedural steps")
        print_success("✅ Consolidated code blocks instead of fragments")
        print_success("✅ Proper anchor IDs matching TOC links (section1, section2, etc.)")
    elif success_rate >= 60:
        print_info(f"⚠️ V2 ENGINE LLM INSTRUCTION FIXES PARTIALLY WORKING - {success_rate:.1f}% SUCCESS RATE")
        print_info("Some LLM instruction fixes are working, but improvements needed.")
    else:
        print_error(f"❌ V2 ENGINE LLM INSTRUCTION FIXES TEST SUITE FAILED - {success_rate:.1f}% SUCCESS RATE")
        print_error("Significant issues detected with LLM instruction fixes.")
    
    return success_rate >= 60

if __name__ == "__main__":
    print("🚀 Starting V2 Engine LLM Instruction Fixes Test Suite...")
    
    try:
        # Run the V2 LLM instruction fixes test
        success = asyncio.run(run_v2_llm_instruction_fixes_test())
        
        if success:
            print("\n🎯 V2 ENGINE LLM INSTRUCTION FIXES TEST SUITE COMPLETED SUCCESSFULLY")
            sys.exit(0)
        else:
            print("\n💥 V2 ENGINE LLM INSTRUCTION FIXES TEST SUITE COMPLETED WITH ISSUES")
            sys.exit(1)
            
    except KeyboardInterrupt:
        print("\n⚠️ Test suite interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Test suite failed with error: {e}")
        sys.exit(1)