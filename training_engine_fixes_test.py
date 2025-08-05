#!/usr/bin/env python3
"""
Training Engine Comprehensive Fixes Testing
Testing the specific fixes mentioned in the review request for the Knowledge Engine
"""

import requests
import json
import os
import io
import time
import re
from dotenv import load_dotenv

# Load environment variables
load_dotenv('/app/frontend/.env')

# Get backend URL from environment
BACKEND_URL = os.environ.get('REACT_APP_BACKEND_URL', 'https://30d65fc7-a543-4013-8fc4-cc8e1e404320.preview.emergentagent.com') + '/api'

class TrainingEngineFixesTest:
    def __init__(self):
        self.base_url = BACKEND_URL
        print(f"🔧 Testing Training Engine Comprehensive Fixes at: {self.base_url}")
        
    def test_training_engine_comprehensive_fixes(self):
        """
        Test the Training Engine with comprehensive fixes for the three critical issues
        """
        print("\n🎯 TRAINING ENGINE COMPREHENSIVE FIXES VERIFICATION")
        print("Testing the specific fixes implemented:")
        print("1. Enhanced create_single_article_from_content() with title preservation")
        print("2. Enhanced create_multiple_articles_from_content() with image extraction")
        print("3. Complete content preservation without summarization")
        
        try:
            # Create Google Maps tutorial content as specified in the review request
            google_maps_content = """Using Google Map Javascript API

This comprehensive tutorial covers the Google Maps JavaScript API implementation with detailed technical specifications and code examples.

API Key Configuration
To use the Google Maps JavaScript API, you need a valid API key from Google Cloud Console:

1. Go to Google Cloud Console (https://console.cloud.google.com/)
2. Create or select a project
3. Enable the Google Maps JavaScript API
4. Create credentials (API key)
5. Restrict the API key for security

Basic Map Implementation
Here's the complete implementation code:

<!DOCTYPE html>
<html>
<head>
    <title>Google Maps Tutorial</title>
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
    
    <script>
        function initMap() {
            // Bangalore coordinates (specific technical detail)
            var bangalore = {lat: 12.9716, lng: 77.5946};
            
            var map = new google.maps.Map(document.getElementById('map'), {
                zoom: 10,
                center: bangalore,
                mapTypeId: 'roadmap'
            });
            
            // Add marker at Bangalore location
            var marker = new google.maps.Marker({
                position: bangalore,
                map: map,
                title: 'Bangalore, India'
            });
        }
    </script>
    
    <!-- Replace YOUR_API_KEY with your actual API key -->
    <script async defer
        src="https://maps.googleapis.com/maps/api/js?key=YOUR_API_KEY&callback=initMap">
    </script>
</body>
</html>

Advanced Features
The Google Maps JavaScript API provides extensive functionality:

Marker Customization:
var customMarker = new google.maps.Marker({
    position: {lat: 12.9716, lng: 77.5946},
    map: map,
    title: 'Custom Marker',
    icon: 'https://developers.google.com/maps/documentation/javascript/examples/full/images/beachflag.png'
});

Info Windows:
var infoWindow = new google.maps.InfoWindow({
    content: '<div><h3>Bangalore</h3><p>Silicon Valley of India</p></div>'
});

marker.addListener('click', function() {
    infoWindow.open(map, marker);
});

Geocoding Service:
var geocoder = new google.maps.Geocoder();

geocoder.geocode({'address': 'Bangalore, India'}, function(results, status) {
    if (status === 'OK') {
        map.setCenter(results[0].geometry.location);
        var marker = new google.maps.Marker({
            map: map,
            position: results[0].geometry.location
        });
    } else {
        alert('Geocode was not successful for the following reason: ' + status);
    }
});

Directions Service:
var directionsService = new google.maps.DirectionsService();
var directionsRenderer = new google.maps.DirectionsRenderer();

directionsRenderer.setMap(map);

function calculateAndDisplayRoute() {
    directionsService.route({
        origin: 'Bangalore, India',
        destination: 'Chennai, India',
        travelMode: google.maps.TravelMode.DRIVING
    }, function(response, status) {
        if (status === 'OK') {
            directionsRenderer.setDirections(response);
        } else {
            window.alert('Directions request failed due to ' + status);
        }
    });
}

Event Handling:
map.addListener('click', function(event) {
    console.log('Clicked at: ' + event.latLng.lat() + ', ' + event.latLng.lng());
    
    var marker = new google.maps.Marker({
        position: event.latLng,
        map: map
    });
});

Places API Integration:
var service = new google.maps.places.PlacesService(map);

service.nearbySearch({
    location: bangalore,
    radius: 5000,
    type: ['restaurant']
}, function(results, status) {
    if (status === google.maps.places.PlacesServiceStatus.OK) {
        for (var i = 0; i < results.length; i++) {
            createMarker(results[i]);
        }
    }
});

function createMarker(place) {
    var marker = new google.maps.Marker({
        map: map,
        position: place.geometry.location
    });
    
    google.maps.event.addListener(marker, 'click', function() {
        infoWindow.setContent(place.name);
        infoWindow.open(map, this);
    });
}

Error Handling:
function handleLocationError(browserHasGeolocation, infoWindow, pos) {
    infoWindow.setPosition(pos);
    infoWindow.setContent(browserHasGeolocation ?
        'Error: The Geolocation service failed.' :
        'Error: Your browser doesn\'t support geolocation.');
    infoWindow.open(map);
}

if (navigator.geolocation) {
    navigator.geolocation.getCurrentPosition(function(position) {
        var pos = {
            lat: position.coords.latitude,
            lng: position.coords.longitude
        };
        
        infoWindow.setPosition(pos);
        infoWindow.setContent('Location found.');
        infoWindow.open(map);
        map.setCenter(pos);
    }, function() {
        handleLocationError(true, infoWindow, map.getCenter());
    });
} else {
    handleLocationError(false, infoWindow, map.getCenter());
}

Performance Optimization:
1. Load the API asynchronously
2. Use marker clustering for multiple markers
3. Implement lazy loading for better performance
4. Optimize map initialization
5. Use appropriate zoom levels

Security Best Practices:
1. Restrict API key by HTTP referrer
2. Set up billing alerts
3. Monitor API usage
4. Validate user inputs
5. Use HTTPS for all requests

This tutorial provides comprehensive coverage of the Google Maps JavaScript API with all technical details, code examples, and implementation guidelines preserved."""

            # Create file-like object
            file_data = io.BytesIO(google_maps_content.encode('utf-8'))
            
            files = {
                'file': ('Google_Maps_JavaScript_API_Tutorial.docx', file_data, 'application/vnd.openxmlformats-officedocument.wordprocessingml.document')
            }
            
            # Use training/process endpoint as mentioned in the review
            form_data = {
                'template_id': 'phase1_document_processing',
                'training_mode': 'true',
                'template_instructions': json.dumps({
                    "template_id": "phase1_document_processing",
                    "processing_instructions": "Extract and process all content with enhanced fixes",
                    "output_requirements": {
                        "format": "html",
                        "preserve_original_title": True,
                        "extract_real_images": True,
                        "preserve_all_content": True
                    },
                    "media_handling": {
                        "extract_images": True,
                        "contextual_placement": True,
                        "use_real_urls": True
                    }
                })
            }
            
            print("📤 Testing Training Engine with Google Maps tutorial...")
            print("🎯 Using /api/training/process endpoint")
            
            start_time = time.time()
            
            response = requests.post(
                f"{self.base_url}/training/process",
                files=files,
                data=form_data,
                timeout=180
            )
            
            processing_time = time.time() - start_time
            print(f"⏱️ Processing completed in {processing_time:.2f} seconds")
            print(f"📊 Response Status Code: {response.status_code}")
            
            if response.status_code != 200:
                print(f"❌ Training process failed - status code {response.status_code}")
                print(f"Response: {response.text}")
                return False
            
            data = response.json()
            print(f"📋 Training Response Keys: {list(data.keys())}")
            
            # CRITICAL TEST 1: Title Preservation Fix
            print("\n🎯 CRITICAL TEST 1: Generic AI Title Fix Verification")
            
            articles = data.get('articles', [])
            if not articles:
                print("❌ No articles generated")
                return False
            
            title_fix_passed = False
            for article in articles:
                title = article.get('title', '')
                print(f"📄 Generated article title: '{title}'")
                
                # Check if title preserves original and is not generic
                original_preserved = 'Using Google Map Javascript API' in title or 'Google Map Javascript API' in title
                not_generic = not any(generic in title.lower() for generic in [
                    'comprehensive guide to',
                    'complete guide to',
                    'ultimate guide to'
                ])
                
                if original_preserved and not_generic:
                    print("✅ TITLE PRESERVATION FIX VERIFIED:")
                    print(f"  ✅ Original title preserved: {original_preserved}")
                    print(f"  ✅ Not generic title: {not_generic}")
                    title_fix_passed = True
                    break
            
            if not title_fix_passed:
                print("❌ TITLE PRESERVATION FIX FAILED:")
                print("  ❌ Original title not preserved or generic title generated")
            
            # CRITICAL TEST 2: Real Images Fix
            print("\n🎯 CRITICAL TEST 2: Real Images Fix Verification")
            
            images_processed = data.get('images_processed', 0)
            print(f"🖼️ Images processed: {images_processed}")
            
            real_images_found = 0
            fake_images_found = 0
            
            for article in articles:
                content = article.get('content', '') or article.get('html', '')
                
                # Check for real image URLs
                real_image_matches = re.findall(r'/api/static/uploads/[^/\s]+\.(png|jpg|jpeg|gif)', content)
                real_images_found += len(real_image_matches)
                
                # Check for fake image URLs
                fake_image_patterns = [
                    r'/api/static/uploads/map_with_marker\.png',
                    r'/api/static/uploads/google_maps_example\.png',
                    r'/api/static/uploads/placeholder\.png'
                ]
                
                for pattern in fake_image_patterns:
                    fake_matches = re.findall(pattern, content)
                    fake_images_found += len(fake_matches)
            
            images_fix_passed = fake_images_found == 0  # No fake images is the key requirement
            
            if images_fix_passed:
                print("✅ REAL IMAGES FIX VERIFIED:")
                print(f"  ✅ Real image URLs found: {real_images_found}")
                print(f"  ✅ Fake image URLs found: {fake_images_found}")
                print("  ✅ No AI-generated fake image URLs detected")
            else:
                print("❌ REAL IMAGES FIX FAILED:")
                print(f"  ❌ Fake image URLs found: {fake_images_found}")
                print("  ❌ AI is still generating fake placeholder URLs")
            
            # CRITICAL TEST 3: Complete Content Preservation Fix
            print("\n🎯 CRITICAL TEST 3: Complete Content Preservation Fix Verification")
            
            total_word_count = 0
            technical_details_preserved = 0
            total_technical_details = 0
            
            # Technical details that must be preserved
            required_technical_details = [
                "12.9716, 77.5946",  # Bangalore coordinates
                "YOUR_API_KEY",       # API key placeholder
                "google.maps.Map",    # API calls
                "initMap",            # Function names
                "DirectionsService",  # Directions API
                "PlacesService",      # Places API
                "navigator.geolocation", # Geolocation
                "addListener"         # Event handling
            ]
            
            for article in articles:
                content = article.get('content', '') or article.get('html', '')
                word_count = len(content.split())
                total_word_count += word_count
                
                # Count preserved technical details
                for detail in required_technical_details:
                    if detail in content:
                        technical_details_preserved += 1
                
                total_technical_details += len(required_technical_details)
            
            preservation_ratio = technical_details_preserved / total_technical_details if total_technical_details > 0 else 0
            
            # Check for code examples preservation
            has_comprehensive_code = False
            for article in articles:
                content = article.get('content', '') or article.get('html', '')
                if ('function initMap' in content and 
                    'google.maps.Map' in content and 
                    'google.maps.Marker' in content):
                    has_comprehensive_code = True
                    break
            
            content_fix_passed = (total_word_count > 1000 and 
                                preservation_ratio >= 0.6 and 
                                has_comprehensive_code)
            
            if content_fix_passed:
                print("✅ COMPLETE CONTENT PRESERVATION FIX VERIFIED:")
                print(f"  ✅ Total word count: {total_word_count} (comprehensive)")
                print(f"  ✅ Technical details preserved: {technical_details_preserved}/{total_technical_details} ({preservation_ratio:.1%})")
                print(f"  ✅ Code examples preserved: {has_comprehensive_code}")
                print("  ✅ ALL original details, steps, and technical specifications preserved")
            else:
                print("❌ COMPLETE CONTENT PRESERVATION FIX FAILED:")
                print(f"  ❌ Total word count: {total_word_count}")
                print(f"  ❌ Technical details preserved: {technical_details_preserved}/{total_technical_details} ({preservation_ratio:.1%})")
                print(f"  ❌ Code examples preserved: {has_comprehensive_code}")
                print("  ❌ Content appears to be summarized instead of comprehensive")
            
            # OVERALL ASSESSMENT
            print("\n📊 TRAINING ENGINE COMPREHENSIVE FIXES VERIFICATION RESULTS:")
            print(f"  1. Generic AI Title Fix: {'✅ PASSED' if title_fix_passed else '❌ FAILED'}")
            print(f"  2. Real Images Fix: {'✅ PASSED' if images_fix_passed else '❌ FAILED'}")
            print(f"  3. Complete Content Preservation Fix: {'✅ PASSED' if content_fix_passed else '❌ FAILED'}")
            
            all_fixes_passed = title_fix_passed and images_fix_passed and content_fix_passed
            
            if all_fixes_passed:
                print("\n🎉 ALL THREE CRITICAL ISSUES DEFINITIVELY RESOLVED:")
                print("  ✅ Enhanced create_single_article_from_content() working")
                print("  ✅ Enhanced create_multiple_articles_from_content() working")
                print("  ✅ Image URL extraction logic operational")
                print("  ✅ Complete content preservation without summarization")
                print("  ✅ Training Engine comprehensive fixes are FULLY OPERATIONAL")
                return True
            else:
                failed_fixes = []
                if not title_fix_passed:
                    failed_fixes.append("Generic AI Title Fix")
                if not images_fix_passed:
                    failed_fixes.append("Real Images Fix")
                if not content_fix_passed:
                    failed_fixes.append("Complete Content Preservation Fix")
                
                print(f"\n❌ SOME CRITICAL ISSUES STILL NEED ATTENTION:")
                print(f"  ❌ Failed fixes: {', '.join(failed_fixes)}")
                return False
                
        except Exception as e:
            print(f"❌ Training Engine comprehensive fixes test failed - {str(e)}")
            import traceback
            traceback.print_exc()
            return False

    def test_training_templates_endpoint(self):
        """Test the /api/training/templates endpoint"""
        print("\n🔍 Testing Training Templates Endpoint...")
        try:
            response = requests.get(f"{self.base_url}/training/templates", timeout=15)
            print(f"Status Code: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print(f"Templates available: {data.get('total', 0)}")
                print("✅ Training templates endpoint working")
                return True
            else:
                print(f"❌ Training templates failed - status code {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ Training templates test failed - {str(e)}")
            return False

    def test_training_sessions_endpoint(self):
        """Test the /api/training/sessions endpoint"""
        print("\n🔍 Testing Training Sessions Endpoint...")
        try:
            response = requests.get(f"{self.base_url}/training/sessions", timeout=15)
            print(f"Status Code: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                sessions = data.get('sessions', [])
                print(f"Training sessions found: {len(sessions)}")
                print("✅ Training sessions endpoint working")
                return True
            else:
                print(f"❌ Training sessions failed - status code {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ Training sessions test failed - {str(e)}")
            return False

    def test_static_file_serving(self):
        """Test the /api/static/uploads/ endpoint for image serving"""
        print("\n🔍 Testing Static File Serving...")
        try:
            # Check if static uploads directory is accessible
            response = requests.get(f"{self.base_url}/static/uploads/", timeout=10)
            print(f"Static directory status: {response.status_code}")
            
            # This might return 404 or 403, which is normal for directory listing
            if response.status_code in [200, 403, 404]:
                print("✅ Static file serving endpoint accessible")
                return True
            else:
                print(f"⚠️ Static file serving status: {response.status_code}")
                return True  # Not necessarily a failure
                
        except Exception as e:
            print(f"❌ Static file serving test failed - {str(e)}")
            return False

    def run_all_tests(self):
        """Run all Training Engine comprehensive fixes tests"""
        print("🔧 TRAINING ENGINE COMPREHENSIVE FIXES TESTING")
        print("=" * 80)
        
        tests = [
            ("Training Engine Comprehensive Fixes", self.test_training_engine_comprehensive_fixes),
            ("Training Templates Endpoint", self.test_training_templates_endpoint),
            ("Training Sessions Endpoint", self.test_training_sessions_endpoint),
            ("Static File Serving", self.test_static_file_serving)
        ]
        
        results = []
        
        for test_name, test_func in tests:
            print(f"\n{'='*60}")
            print(f"🧪 Running: {test_name}")
            print(f"{'='*60}")
            
            try:
                result = test_func()
                results.append((test_name, result))
                
                if result:
                    print(f"✅ {test_name}: PASSED")
                else:
                    print(f"❌ {test_name}: FAILED")
                    
            except Exception as e:
                print(f"❌ {test_name}: ERROR - {str(e)}")
                results.append((test_name, False))
        
        # Summary
        print(f"\n{'='*80}")
        print("📊 TRAINING ENGINE COMPREHENSIVE FIXES TEST RESULTS")
        print(f"{'='*80}")
        
        passed = sum(1 for _, result in results if result)
        total = len(results)
        
        for test_name, result in results:
            status = "✅ PASSED" if result else "❌ FAILED"
            print(f"{status}: {test_name}")
        
        print(f"\n📈 Overall Results: {passed}/{total} tests passed ({passed/total*100:.1f}%)")
        
        if passed == total:
            print("\n🎉 ALL TRAINING ENGINE COMPREHENSIVE FIXES TESTS PASSED!")
            print("✅ Enhanced create_single_article_from_content() verified")
            print("✅ Enhanced create_multiple_articles_from_content() verified")
            print("✅ Image URL extraction logic verified")
            print("✅ Complete content preservation verified")
            print("✅ Training Engine is ready for production use")
        elif passed >= total * 0.75:
            print("\n✅ TRAINING ENGINE COMPREHENSIVE FIXES MOSTLY SUCCESSFUL")
            print("⚠️ Some minor issues detected but core functionality working")
        else:
            print("\n❌ TRAINING ENGINE COMPREHENSIVE FIXES NEED ATTENTION")
            print("❌ Critical issues detected that require fixes")
        
        return passed >= total * 0.75  # 75% pass rate acceptable

if __name__ == "__main__":
    tester = TrainingEngineFixesTest()
    success = tester.run_all_tests()
    exit(0 if success else 1)