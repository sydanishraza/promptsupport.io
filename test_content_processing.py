#!/usr/bin/env python3
"""
Test content processing to identify where source content is being lost
"""

import requests
import json
import time

BACKEND_URL = "https://22c64acd-5965-4f32-bb15-b795b8db8eab.preview.emergentagent.com"
API_BASE = f"{BACKEND_URL}/api"

def test_content_processing():
    """Test content processing with real Google Maps tutorial content"""
    
    test_content = """
# Google Maps JavaScript API Tutorial

## Introduction
This tutorial will teach you how to integrate Google Maps into your web application using the JavaScript API.

## Step 1: Get API Key
First, you need to get an API key from Google Cloud Console:
1. Go to Google Cloud Console
2. Create a new project
3. Enable Maps JavaScript API
4. Create credentials

## Step 2: Basic Implementation
Here is the basic HTML structure:

```html
<!DOCTYPE html>
<html>
<head>
    <title>My Google Map</title>
</head>
<body>
    <div id="map" style="height: 400px;"></div>
    <script>
        function initMap() {
            var map = new google.maps.Map(document.getElementById('map'), {
                zoom: 10,
                center: {lat: -34.397, lng: 150.644}
            });
        }
    </script>
    <script src="https://maps.googleapis.com/maps/api/js?key=YOUR_API_KEY&callback=initMap"></script>
</body>
</html>
```

## Step 3: Adding Markers
You can add markers to your map:

```javascript
var marker = new google.maps.Marker({
    position: {lat: -34.397, lng: 150.644},
    map: map,
    title: 'Hello World!'
});
```

## Troubleshooting
Common issues and solutions:
- API key not working: Check if the API is enabled
- Map not loading: Verify the callback function name
- Markers not showing: Check the coordinates
"""

    print('Testing content processing with real Google Maps tutorial content...')
    print(f'Content length: {len(test_content)} characters')

    # Try to find the correct endpoint for text processing
    endpoints_to_try = [
        '/content/process-text',
        '/content/upload-text', 
        '/content/process',
        '/upload/text',
        '/process-content',
        '/content/upload'  # This might be for file upload
    ]

    for endpoint in endpoints_to_try:
        try:
            print(f'\nTrying endpoint: {endpoint}')
            
            if endpoint == '/content/upload':
                # Try as file upload
                files = {'file': ('test_tutorial.txt', test_content, 'text/plain')}
                response = requests.post(f'{API_BASE}{endpoint}', files=files, timeout=30)
            else:
                # Try as JSON payload
                payload = {
                    'content': test_content,
                    'filename': 'google_maps_tutorial_test.txt'
                }
                response = requests.post(f'{API_BASE}{endpoint}', json=payload, timeout=30)
            
            print(f'Status: {response.status_code}')
            
            if response.status_code == 200:
                print('✅ SUCCESS! Found working endpoint')
                result = response.json()
                print(f'Response keys: {list(result.keys())}')
                if 'job_id' in result:
                    print(f'Job ID: {result["job_id"]}')
                    return result['job_id']
                break
            elif response.status_code == 404:
                print('❌ Endpoint not found')
            else:
                print(f'❌ Error: {response.text[:200]}')
                
        except Exception as e:
            print(f'❌ Exception: {e}')

    return None

def check_available_endpoints():
    """Check what endpoints are available"""
    print('\n--- Checking available endpoints ---')
    
    # Common API endpoints to check
    endpoints_to_check = [
        '/health',
        '/content-library',
        '/docs',
        '/openapi.json'
    ]
    
    for endpoint in endpoints_to_check:
        try:
            response = requests.get(f'{API_BASE}{endpoint}', timeout=10)
            print(f'{endpoint}: Status {response.status_code}')
            if response.status_code == 200 and endpoint == '/openapi.json':
                # Try to extract available endpoints from OpenAPI spec
                try:
                    spec = response.json()
                    paths = spec.get('paths', {})
                    print(f'Available paths: {list(paths.keys())[:10]}...')  # Show first 10
                except:
                    pass
        except Exception as e:
            print(f'{endpoint}: Error - {e}')

if __name__ == "__main__":
    job_id = test_content_processing()
    check_available_endpoints()
    
    if job_id:
        print(f'\n✅ Content processing started with job ID: {job_id}')
        print('Monitor this job to see if real content is processed correctly')
    else:
        print('\n❌ Could not start content processing - endpoint not found')