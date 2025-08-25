#!/usr/bin/env python3
"""
CRITICAL ENHANCED FEATURES FIX VERIFICATION
Tests the ensure_enhanced_features() function implementation for:
1. Mini-TOC present at start (should be 100%)
2. Enhanced Code Blocks with copy buttons
3. Callouts present (callout-tip or other types)
4. Enhanced List Classes (doc-list CSS classes)
5. Cross-References (see-also references and cross-ref links)
6. Anchor IDs on headings (H2 tags with proper id attributes)
"""

import requests
import json
import os
import time
import re
from bs4 import BeautifulSoup
from dotenv import load_dotenv

# Load environment variables
load_dotenv('/app/frontend/.env')

# Get backend URL from environment
BACKEND_URL = os.environ.get('REACT_APP_BACKEND_URL', 'https://content-formatter.preview.emergentagent.com') + '/api'

class CriticalEnhancedFeaturesTest:
    def __init__(self):
        self.base_url = BACKEND_URL
        self.test_results = {
            "mini_toc_present": {"passed": 0, "total": 0, "percentage": 0},
            "enhanced_code_blocks": {"passed": 0, "total": 0, "percentage": 0},
            "callouts_present": {"passed": 0, "total": 0, "percentage": 0},
            "enhanced_list_classes": {"passed": 0, "total": 0, "percentage": 0},
            "cross_references": {"passed": 0, "total": 0, "percentage": 0},
            "anchor_ids_on_headings": {"passed": 0, "total": 0, "percentage": 0}
        }
        print(f"🔥 CRITICAL ENHANCED FEATURES TESTING at: {self.base_url}")
        
    def process_sample_content(self, content: str, description: str) -> str:
        """Process sample content through the backend and return generated article"""
        try:
            print(f"\n📝 PROCESSING SAMPLE: {description}")
            print(f"Content length: {len(content)} characters")
            
            # Create multipart form data
            files = {
                'file': (f'test_{description.lower().replace(" ", "_")}.txt', content, 'text/plain')
            }
            
            # Process content
            response = requests.post(
                f"{self.base_url}/upload",
                files=files,
                timeout=60
            )
            
            if response.status_code == 200:
                result = response.json()
                job_id = result.get('job_id')
                print(f"✅ Processing started with job ID: {job_id}")
                
                # Wait for processing to complete
                time.sleep(8)
                
                # Get the generated articles from Content Library
                lib_response = requests.get(f"{self.base_url}/content-library")
                if lib_response.status_code == 200:
                    library_data = lib_response.json()
                    articles = library_data.get('articles', [])
                    
                    if articles:
                        # Find the most recent article (should be our test article)
                        latest_article = max(articles, key=lambda x: x.get('created_at', ''))
                        print(f"📄 Retrieved article: {latest_article['title']}")
                        return latest_article['content']
                    else:
                        print("❌ No articles found in Content Library")
                        return None
                else:
                    print(f"❌ Failed to retrieve Content Library: {lib_response.status_code}")
                    return None
            else:
                print(f"❌ Processing failed: {response.status_code}")
                return None
                
        except Exception as e:
            print(f"❌ Error processing sample content: {e}")
            return None
    
    def analyze_mini_toc(self, content: str, description: str) -> bool:
        """Test 1: Mini-TOC present at start - should be 100%"""
        self.test_results["mini_toc_present"]["total"] += 1
        
        soup = BeautifulSoup(content, 'html.parser')
        
        # Look for mini-toc class
        mini_toc = soup.find('div', class_='mini-toc')
        
        # Look for TOC-like structures at the beginning
        first_1000_chars = content[:1000].lower()
        toc_indicators = [
            'contents', 'table of contents', 'mini-toc', 'toc-list',
            '📋 contents', '📋 table of contents'
        ]
        
        has_toc_indicators = any(indicator in first_1000_chars for indicator in toc_indicators)
        
        # Look for anchor links in lists (TOC navigation)
        anchor_links = soup.find_all('a', href=re.compile(r'^#'))
        has_navigation_links = len(anchor_links) > 0
        
        # Check for list with navigation structure
        toc_lists = soup.find_all('ul', class_=re.compile(r'toc'))
        
        passed = bool(mini_toc or (has_toc_indicators and has_navigation_links) or toc_lists)
        
        if passed:
            self.test_results["mini_toc_present"]["passed"] += 1
            
        print(f"{'✅' if passed else '❌'} Mini-TOC Test ({description}): {'PASSED' if passed else 'FAILED'}")
        print(f"   - Mini-TOC div: {bool(mini_toc)}")
        print(f"   - TOC indicators: {has_toc_indicators}")
        print(f"   - Anchor links: {len(anchor_links)}")
        print(f"   - TOC lists: {len(toc_lists)}")
        
        return passed
    
    def analyze_enhanced_code_blocks(self, content: str, description: str) -> bool:
        """Test 2: Enhanced Code Blocks with copy buttons"""
        self.test_results["enhanced_code_blocks"]["total"] += 1
        
        soup = BeautifulSoup(content, 'html.parser')
        
        # Look for enhanced code block containers
        code_containers = soup.find_all('div', class_='code-block-container')
        copy_buttons = soup.find_all('button', class_='copy-code-btn')
        code_headers = soup.find_all('div', class_='code-header')
        
        # Count total code blocks
        all_code_blocks = soup.find_all('pre')
        basic_code_blocks = [block for block in all_code_blocks if not block.find_parent('div', class_='code-block-container')]
        
        total_code_blocks = len(all_code_blocks)
        enhanced_code_blocks = len(code_containers)
        
        # If there are code blocks, they should be enhanced
        if total_code_blocks > 0:
            passed = enhanced_code_blocks > 0 and len(copy_buttons) > 0
        else:
            passed = True  # No code blocks to enhance
            
        if passed:
            self.test_results["enhanced_code_blocks"]["passed"] += 1
            
        print(f"{'✅' if passed else '❌'} Enhanced Code Blocks Test ({description}): {'PASSED' if passed else 'FAILED'}")
        print(f"   - Total code blocks: {total_code_blocks}")
        print(f"   - Enhanced containers: {enhanced_code_blocks}")
        print(f"   - Copy buttons: {len(copy_buttons)}")
        print(f"   - Code headers: {len(code_headers)}")
        
        return passed
    
    def analyze_callouts(self, content: str, description: str) -> bool:
        """Test 3: Callouts present (callout-tip or other types)"""
        self.test_results["callouts_present"]["total"] += 1
        
        soup = BeautifulSoup(content, 'html.parser')
        
        # Look for callout elements
        callouts = soup.find_all('div', class_=re.compile(r'callout'))
        callout_tips = soup.find_all('div', class_='callout-tip')
        callout_titles = soup.find_all('div', class_='callout-title')
        callout_content = soup.find_all('div', class_='callout-content')
        
        # Look for callout-like visual indicators
        callout_emojis = re.findall(r'(💡|⚠️|📝|🔥|⭐|🎯|📋)', content)
        
        passed = len(callouts) > 0 or len(callout_emojis) > 2  # Should have callouts or visual indicators
        
        if passed:
            self.test_results["callouts_present"]["passed"] += 1
            
        print(f"{'✅' if passed else '❌'} Callouts Test ({description}): {'PASSED' if passed else 'FAILED'}")
        print(f"   - Callout divs: {len(callouts)}")
        print(f"   - Callout tips: {len(callout_tips)}")
        print(f"   - Callout titles: {len(callout_titles)}")
        print(f"   - Visual indicators: {len(callout_emojis)}")
        
        return passed
    
    def analyze_enhanced_list_classes(self, content: str, description: str) -> bool:
        """Test 4: Enhanced List Classes (doc-list CSS classes)"""
        self.test_results["enhanced_list_classes"]["total"] += 1
        
        soup = BeautifulSoup(content, 'html.parser')
        
        # Find all lists
        ordered_lists = soup.find_all('ol')
        unordered_lists = soup.find_all('ul')
        total_lists = len(ordered_lists) + len(unordered_lists)
        
        # Find lists with enhanced classes
        doc_list_ordered = soup.find_all('ol', class_=re.compile(r'doc-list.*ordered'))
        doc_list_unordered = soup.find_all('ul', class_=re.compile(r'doc-list.*unordered'))
        doc_list_any = soup.find_all(['ol', 'ul'], class_=re.compile(r'doc-list'))
        
        enhanced_lists = len(doc_list_any)
        
        if total_lists > 0:
            enhancement_ratio = enhanced_lists / total_lists
            passed = enhancement_ratio >= 0.8  # At least 80% of lists should have enhanced classes
        else:
            passed = True  # No lists to enhance
            enhancement_ratio = 1.0
            
        if passed:
            self.test_results["enhanced_list_classes"]["passed"] += 1
            
        print(f"{'✅' if passed else '❌'} Enhanced List Classes Test ({description}): {'PASSED' if passed else 'FAILED'}")
        print(f"   - Total lists: {total_lists}")
        print(f"   - Enhanced lists: {enhanced_lists}")
        print(f"   - Enhancement ratio: {enhancement_ratio:.1%}")
        print(f"   - Doc-list ordered: {len(doc_list_ordered)}")
        print(f"   - Doc-list unordered: {len(doc_list_unordered)}")
        
        return passed
    
    def analyze_cross_references(self, content: str, description: str) -> bool:
        """Test 5: Cross-References (see-also references and cross-ref links)"""
        self.test_results["cross_references"]["total"] += 1
        
        soup = BeautifulSoup(content, 'html.parser')
        
        # Look for cross-reference elements
        cross_ref_links = soup.find_all('a', class_='cross-ref')
        see_also_sections = soup.find_all(class_='see-also')
        
        # Look for cross-reference patterns in text
        cross_ref_patterns = re.findall(r'(see also|refer to|check out|learn more|cross-ref)', content.lower())
        
        # Look for anchor links (internal navigation)
        anchor_links = soup.find_all('a', href=re.compile(r'^#'))
        
        # Look for related links sections
        related_links = soup.find_all(class_='related-links')
        
        passed = (len(cross_ref_links) > 0 or len(see_also_sections) > 0 or 
                 len(cross_ref_patterns) > 0 or len(anchor_links) > 0 or len(related_links) > 0)
        
        if passed:
            self.test_results["cross_references"]["passed"] += 1
            
        print(f"{'✅' if passed else '❌'} Cross-References Test ({description}): {'PASSED' if passed else 'FAILED'}")
        print(f"   - Cross-ref links: {len(cross_ref_links)}")
        print(f"   - See-also sections: {len(see_also_sections)}")
        print(f"   - Cross-ref patterns: {len(cross_ref_patterns)}")
        print(f"   - Anchor links: {len(anchor_links)}")
        print(f"   - Related links: {len(related_links)}")
        
        return passed
    
    def analyze_anchor_ids_on_headings(self, content: str, description: str) -> bool:
        """Test 6: Anchor IDs on headings (H2 tags with proper id attributes)"""
        self.test_results["anchor_ids_on_headings"]["total"] += 1
        
        soup = BeautifulSoup(content, 'html.parser')
        
        # Find all H2 headings
        h2_headings = soup.find_all('h2')
        h2_with_ids = soup.find_all('h2', id=True)
        
        # Also check H3 headings for completeness
        h3_headings = soup.find_all('h3')
        h3_with_ids = soup.find_all('h3', id=True)
        
        total_headings = len(h2_headings) + len(h3_headings)
        headings_with_ids = len(h2_with_ids) + len(h3_with_ids)
        
        if total_headings > 0:
            id_ratio = headings_with_ids / total_headings
            passed = id_ratio >= 0.5  # At least 50% of headings should have IDs
        else:
            passed = True  # No headings to enhance
            id_ratio = 1.0
            
        if passed:
            self.test_results["anchor_ids_on_headings"]["passed"] += 1
            
        # Sample some IDs for verification
        sample_ids = [h.get('id') for h in h2_with_ids[:3] if h.get('id')]
        
        print(f"{'✅' if passed else '❌'} Anchor IDs on Headings Test ({description}): {'PASSED' if passed else 'FAILED'}")
        print(f"   - Total H2 headings: {len(h2_headings)}")
        print(f"   - H2 with IDs: {len(h2_with_ids)}")
        print(f"   - Total H3 headings: {len(h3_headings)}")
        print(f"   - H3 with IDs: {len(h3_with_ids)}")
        print(f"   - ID ratio: {id_ratio:.1%}")
        print(f"   - Sample IDs: {sample_ids}")
        
        return passed
    
    def run_comprehensive_test(self):
        """Run comprehensive enhanced features testing"""
        print("🔥 STARTING CRITICAL ENHANCED FEATURES FIX VERIFICATION")
        print("=" * 80)
        print("Testing the ensure_enhanced_features() function implementation")
        print("Expected: 100% compliance with all enhanced features")
        print("=" * 80)
        
        # Test Case 1: Tutorial Content with Code Blocks
        tutorial_content = """
# Google Maps JavaScript API Tutorial

This comprehensive tutorial will guide you through implementing Google Maps in your web application.

## Prerequisites

Before starting, you'll need:
- Basic knowledge of HTML and JavaScript
- A Google Cloud Platform account
- An API key for Google Maps

## Step 1: Setup

First, include the Google Maps API in your HTML:

```html
<script src="https://maps.googleapis.com/maps/api/js?key=YOUR_API_KEY"></script>
```

## Step 2: Initialize the Map

Create a basic map instance:

```javascript
function initMap() {
    const map = new google.maps.Map(document.getElementById('map'), {
        zoom: 10,
        center: { lat: -34.397, lng: 150.644 }
    });
}
```

## Advanced Features

The Google Maps API provides many advanced features:

1. Custom markers and icons
2. Info windows and popups
3. Geocoding and reverse geocoding
4. Directions and routing
5. Street View integration

## Best Practices

When implementing Google Maps:

- Always handle API errors gracefully
- Optimize marker clustering for performance
- Use appropriate zoom levels
- Consider mobile responsiveness

## Troubleshooting

Common issues and their solutions:

- API key not working: Check your API key configuration
- Map not loading: Verify the script tag is correct
- Markers not appearing: Check coordinate format
"""
        
        processed_content = self.process_sample_content(tutorial_content, "Tutorial with Code")
        if processed_content:
            print(f"\n🔍 ANALYZING TUTORIAL CONTENT ({len(processed_content)} chars)")
            self.analyze_mini_toc(processed_content, "Tutorial with Code")
            self.analyze_enhanced_code_blocks(processed_content, "Tutorial with Code")
            self.analyze_callouts(processed_content, "Tutorial with Code")
            self.analyze_enhanced_list_classes(processed_content, "Tutorial with Code")
            self.analyze_cross_references(processed_content, "Tutorial with Code")
            self.analyze_anchor_ids_on_headings(processed_content, "Tutorial with Code")
        
        # Test Case 2: Reference Documentation
        reference_content = """
# API Reference Documentation

Complete reference for the Content Management System API.

## Authentication

All API requests require authentication using Bearer tokens.

### Required Headers

- Authorization: Bearer YOUR_TOKEN
- Content-Type: application/json
- Accept: application/json

## Endpoints Overview

The API provides the following main endpoints:

1. Articles Management
2. User Authentication
3. File Upload
4. Content Processing

## Articles Endpoints

### GET /api/articles

Retrieve all articles with optional filtering.

Query Parameters:
- limit: Maximum number of articles (default: 50)
- offset: Starting position (default: 0)
- status: Filter by status (published, draft)
- tags: Filter by tags (comma-separated)

### POST /api/articles

Create a new article.

Required Fields:
- title: Article title (string, max 200 chars)
- content: Article content (string, HTML allowed)
- status: Article status (published or draft)

Optional Fields:
- tags: Array of tags
- metadata: Additional metadata object

## Error Handling

The API returns standard HTTP status codes:

- 200: Success
- 201: Created
- 400: Bad Request
- 401: Unauthorized
- 403: Forbidden
- 404: Not Found
- 500: Internal Server Error

## Rate Limiting

API calls are limited to:
- 1000 requests per hour for authenticated users
- 100 requests per hour for unauthenticated users
"""
        
        processed_content = self.process_sample_content(reference_content, "API Reference")
        if processed_content:
            print(f"\n🔍 ANALYZING REFERENCE CONTENT ({len(processed_content)} chars)")
            self.analyze_mini_toc(processed_content, "API Reference")
            self.analyze_enhanced_code_blocks(processed_content, "API Reference")
            self.analyze_callouts(processed_content, "API Reference")
            self.analyze_enhanced_list_classes(processed_content, "API Reference")
            self.analyze_cross_references(processed_content, "API Reference")
            self.analyze_anchor_ids_on_headings(processed_content, "API Reference")
        
        # Test Case 3: Mixed Content Guide
        mixed_content = """
# Complete Setup and Configuration Guide

This comprehensive guide covers everything you need to set up and configure the system.

## Overview

The setup process involves several key phases:

1. Environment preparation
2. Software installation
3. System configuration
4. Testing and validation
5. Production deployment

## System Requirements

### Hardware Requirements

- CPU: 4 cores minimum, 8 cores recommended
- RAM: 16GB minimum, 32GB recommended
- Storage: 100GB SSD minimum
- Network: Stable internet connection

### Software Requirements

- Operating System: Ubuntu 20.04+ or CentOS 8+
- Docker: Version 20.10+
- Docker Compose: Version 1.29+
- Git: Latest version

## Installation Steps

### Step 1: Environment Setup

```bash
# Update system packages
sudo apt update && sudo apt upgrade -y

# Install required packages
sudo apt install -y curl wget git
```

### Step 2: Docker Installation

```bash
# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Add user to docker group
sudo usermod -aG docker $USER
```

### Step 3: Application Setup

```bash
# Clone the repository
git clone https://github.com/example/app.git
cd app

# Copy configuration template
cp .env.example .env
```

## Configuration

### Environment Variables

Edit the .env file with your settings:

```bash
# Database configuration
DB_HOST=localhost
DB_PORT=5432
DB_NAME=myapp
DB_USER=admin
DB_PASSWORD=secure_password

# API configuration
API_KEY=your_api_key_here
API_ENDPOINT=https://api.example.com

# Security settings
JWT_SECRET=your_jwt_secret
ENCRYPTION_KEY=your_encryption_key
```

## Testing Your Setup

Run the following commands to verify everything is working:

```bash
# Start the application
docker-compose up -d

# Check service status
docker-compose ps

# Run health checks
curl http://localhost:8080/health
```

## Common Issues

### Port Conflicts

If you encounter port conflicts:
- Check which processes are using the ports
- Modify the port configuration in docker-compose.yml
- Restart the services

### Permission Errors

For permission issues:
- Ensure proper file ownership
- Check Docker group membership
- Verify directory permissions

### Database Connection Issues

If database connections fail:
- Verify database credentials
- Check network connectivity
- Review firewall settings
"""
        
        processed_content = self.process_sample_content(mixed_content, "Mixed Content Guide")
        if processed_content:
            print(f"\n🔍 ANALYZING MIXED CONTENT ({len(processed_content)} chars)")
            self.analyze_mini_toc(processed_content, "Mixed Content Guide")
            self.analyze_enhanced_code_blocks(processed_content, "Mixed Content Guide")
            self.analyze_callouts(processed_content, "Mixed Content Guide")
            self.analyze_enhanced_list_classes(processed_content, "Mixed Content Guide")
            self.analyze_cross_references(processed_content, "Mixed Content Guide")
            self.analyze_anchor_ids_on_headings(processed_content, "Mixed Content Guide")
        
        # Generate final report
        self.generate_final_report()
    
    def generate_final_report(self):
        """Generate comprehensive test report"""
        print("\n" + "=" * 80)
        print("🎯 CRITICAL ENHANCED FEATURES FIX VERIFICATION RESULTS")
        print("=" * 80)
        
        # Calculate percentages
        for feature_name, results in self.test_results.items():
            if results["total"] > 0:
                results["percentage"] = (results["passed"] / results["total"]) * 100
            else:
                results["percentage"] = 0
        
        # Display results
        print("\n📊 DETAILED RESULTS:")
        
        overall_passed = 0
        overall_total = 0
        
        for feature_name, results in self.test_results.items():
            passed = results["passed"]
            total = results["total"]
            percentage = results["percentage"]
            
            overall_passed += passed
            overall_total += total
            
            status_icon = "✅" if percentage == 100 else "⚠️" if percentage >= 80 else "❌"
            feature_display = feature_name.replace('_', ' ').title()
            
            print(f"{status_icon} {feature_display}: {passed}/{total} ({percentage:.1f}%)")
        
        overall_percentage = (overall_passed / max(1, overall_total)) * 100
        
        print(f"\n🏆 OVERALL ENHANCED FEATURES COMPLIANCE")
        print(f"   Tests Passed: {overall_passed}/{overall_total}")
        print(f"   Success Rate: {overall_percentage:.1f}%")
        
        # Determine final status
        if overall_percentage == 100:
            status = "✅ PERFECT - All enhanced features working at 100% compliance!"
            recommendation = "The ensure_enhanced_features() function is working perfectly."
        elif overall_percentage >= 90:
            status = "✅ EXCELLENT - Enhanced features working very well"
            recommendation = "Minor improvements needed for 100% compliance."
        elif overall_percentage >= 80:
            status = "⚠️ GOOD - Most enhanced features working"
            recommendation = "Some enhanced features need attention to reach target compliance."
        elif overall_percentage >= 60:
            status = "⚠️ PARTIAL - Enhanced features partially working"
            recommendation = "Significant improvements needed in ensure_enhanced_features() function."
        else:
            status = "❌ CRITICAL - Enhanced features not working properly"
            recommendation = "Major fixes required in ensure_enhanced_features() implementation."
        
        print(f"   Status: {status}")
        print(f"   Recommendation: {recommendation}")
        
        print("\n" + "=" * 80)
        print("🔥 CRITICAL VERIFICATION COMPLETE")
        print("=" * 80)
        
        return overall_percentage

def main():
    """Main test execution"""
    tester = CriticalEnhancedFeaturesTest()
    tester.run_comprehensive_test()

if __name__ == "__main__":
    main()