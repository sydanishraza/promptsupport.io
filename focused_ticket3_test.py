#!/usr/bin/env python3
"""
Focused TICKET 3 Testing - Universal Bookmarks & Durable Links System
Quick focused test of TICKET 3 implementation with correct endpoints
"""

import requests
import json
import time
import sys
import re
from datetime import datetime

# Use configured backend URL from environment
import os
BACKEND_URL = os.getenv('REACT_APP_BACKEND_URL', 'https://content-formatter.preview.emergentagent.com')
API_BASE = f"{BACKEND_URL}/api"

print(f"🧪 FOCUSED TICKET 3 TESTING")
print(f"🌐 Backend URL: {BACKEND_URL}")
print(f"📡 API Base: {API_BASE}")
print("=" * 60)

def test_ticket3_endpoints():
    """Test TICKET 3 API endpoints"""
    print("🔧 Testing TICKET 3 API Endpoints")
    
    endpoints = [
        {
            'name': 'Backfill Bookmarks',
            'url': f"{API_BASE}/ticket3/backfill-bookmarks",
            'method': 'POST',
            'data': {'limit': 1}
        },
        {
            'name': 'Validate Cross-Document Links', 
            'url': f"{API_BASE}/ticket3/validate-cross-document-links",
            'method': 'POST',
            'data': {
                'doc_uid': 'test123',
                'xrefs': ['test#anchor1'],
                'related_links': ['test#anchor2']
            }
        },
        {
            'name': 'Build Cross-Document Link',
            'url': f"{API_BASE}/ticket3/build-link",
            'method': 'GET',
            'params': {
                'doc_uid': 'test123',
                'anchor': 'test-anchor',
                'environment': 'production'
            }
        }
    ]
    
    results = []
    
    for endpoint in endpoints:
        try:
            print(f"  Testing {endpoint['name']}...")
            
            if endpoint['method'] == 'POST':
                response = requests.post(
                    endpoint['url'], 
                    json=endpoint['data'], 
                    timeout=10
                )
            else:
                response = requests.get(
                    endpoint['url'], 
                    params=endpoint.get('params', {}), 
                    timeout=10
                )
            
            # Check if endpoint exists and responds
            endpoint_exists = response.status_code != 404
            endpoint_working = response.status_code in [200, 400, 422]
            
            result = {
                'name': endpoint['name'],
                'exists': endpoint_exists,
                'working': endpoint_working,
                'status_code': response.status_code,
                'response_size': len(response.text) if response.text else 0
            }
            
            if endpoint_working and response.text:
                try:
                    json_response = response.json()
                    result['has_json'] = True
                    result['response_keys'] = list(json_response.keys()) if isinstance(json_response, dict) else []
                except:
                    result['has_json'] = False
            
            results.append(result)
            
            status = "✅" if endpoint_working else "❌"
            print(f"    {status} {endpoint['name']}: {response.status_code}")
            
        except Exception as e:
            results.append({
                'name': endpoint['name'],
                'exists': False,
                'working': False,
                'error': str(e)
            })
            print(f"    ❌ {endpoint['name']}: Exception - {str(e)}")
    
    return results

def test_content_processing_with_ticket3():
    """Test content processing to see if TICKET 3 fields are generated"""
    print("🔧 Testing Content Processing for TICKET 3 Fields")
    
    test_content = """
    <h2>Google Maps JavaScript API Tutorial</h2>
    <p>Learn how to integrate Google Maps into your web applications.</p>
    
    <h3>Getting Started</h3>
    <p>First, you need to obtain an API key.</p>
    
    <h3>Creating Your First Map</h3>
    <p>Let's create a basic map implementation.</p>
    """
    
    try:
        print("  Processing test content...")
        response = requests.post(
            f"{API_BASE}/content/process",
            json={
                "content": test_content,
                "content_type": "text",
                "metadata": {
                    "title": "Google Maps API Tutorial",
                    "test_type": "ticket3_fields_test"
                }
            },
            timeout=20
        )
        
        if response.status_code == 200:
            result = response.json()
            
            if 'articles' in result and len(result['articles']) > 0:
                article = result['articles'][0]
                
                # Check for TICKET 3 fields
                ticket3_fields = {
                    'doc_uid': 'doc_uid' in article,
                    'doc_slug': 'doc_slug' in article,
                    'headings_registry': 'headings_registry' in article,
                    'xrefs': 'xrefs' in article,
                    'related_links': 'related_links' in article
                }
                
                print("  TICKET 3 Fields Found:")
                for field, found in ticket3_fields.items():
                    status = "✅" if found else "❌"
                    print(f"    {status} {field}: {found}")
                    if found and field in article:
                        value = article[field]
                        if isinstance(value, list):
                            print(f"        (list with {len(value)} items)")
                        elif isinstance(value, str):
                            print(f"        (string: {value[:50]}...)")
                
                # Check specific field validity
                if ticket3_fields['doc_uid'] and article['doc_uid']:
                    doc_uid = article['doc_uid']
                    uid_valid = len(doc_uid) == 26 and doc_uid.startswith('01JZ')
                    print(f"    📋 doc_uid format valid: {uid_valid} ({doc_uid})")
                
                if ticket3_fields['headings_registry'] and article['headings_registry']:
                    registry = article['headings_registry']
                    registry_valid = len(registry) > 0 and all('id' in entry for entry in registry)
                    print(f"    📋 headings_registry valid: {registry_valid} ({len(registry)} entries)")
                
                fields_found = sum(ticket3_fields.values())
                success_rate = fields_found / len(ticket3_fields)
                
                return {
                    'processing_successful': True,
                    'fields_found': fields_found,
                    'total_fields': len(ticket3_fields),
                    'success_rate': success_rate,
                    'article_generated': True
                }
            else:
                print("  ❌ No articles generated")
                return {'processing_successful': False, 'error': 'No articles generated'}
        else:
            print(f"  ❌ Processing failed: {response.status_code}")
            return {'processing_successful': False, 'error': f'HTTP {response.status_code}'}
            
    except Exception as e:
        print(f"  ❌ Exception: {str(e)}")
        return {'processing_successful': False, 'error': str(e)}

def test_content_library_ticket3_data():
    """Check if content library has articles with TICKET 3 data"""
    print("🔧 Testing Content Library for TICKET 3 Data")
    
    try:
        response = requests.get(f"{API_BASE}/content-library", timeout=10)
        
        if response.status_code == 200:
            result = response.json()
            
            if 'articles' in result and len(result['articles']) > 0:
                articles = result['articles']
                
                # Check first few articles for TICKET 3 fields
                ticket3_articles = 0
                checked_articles = min(3, len(articles))
                
                for i, article in enumerate(articles[:checked_articles]):
                    has_doc_uid = 'doc_uid' in article and article['doc_uid']
                    has_doc_slug = 'doc_slug' in article and article['doc_slug'] 
                    has_headings_registry = 'headings_registry' in article
                    
                    ticket3_score = sum([has_doc_uid, has_doc_slug, has_headings_registry])
                    
                    if ticket3_score >= 2:  # At least 2 out of 3 fields
                        ticket3_articles += 1
                    
                    print(f"  Article {i+1}: doc_uid={has_doc_uid}, doc_slug={has_doc_slug}, registry={has_headings_registry}")
                
                persistence_rate = ticket3_articles / checked_articles
                print(f"  📊 TICKET 3 articles: {ticket3_articles}/{checked_articles} ({persistence_rate:.1%})")
                
                return {
                    'library_accessible': True,
                    'articles_found': len(articles),
                    'ticket3_articles': ticket3_articles,
                    'checked_articles': checked_articles,
                    'persistence_rate': persistence_rate
                }
            else:
                print("  ❌ No articles in content library")
                return {'library_accessible': True, 'articles_found': 0}
        else:
            print(f"  ❌ Content library error: {response.status_code}")
            return {'library_accessible': False, 'error': f'HTTP {response.status_code}'}
            
    except Exception as e:
        print(f"  ❌ Exception: {str(e)}")
        return {'library_accessible': False, 'error': str(e)}

def main():
    """Run focused TICKET 3 tests"""
    print("🚀 Starting Focused TICKET 3 Testing")
    print("=" * 60)
    
    # Test 1: API Endpoints
    endpoint_results = test_ticket3_endpoints()
    print()
    
    # Test 2: Content Processing
    processing_results = test_content_processing_with_ticket3()
    print()
    
    # Test 3: Content Library Data
    library_results = test_content_library_ticket3_data()
    print()
    
    # Summary
    print("=" * 60)
    print("📊 FOCUSED TICKET 3 TEST SUMMARY")
    print("=" * 60)
    
    # Endpoint summary
    working_endpoints = sum(1 for r in endpoint_results if r.get('working', False))
    total_endpoints = len(endpoint_results)
    endpoint_rate = working_endpoints / total_endpoints if total_endpoints > 0 else 0
    
    print(f"🔗 API Endpoints: {working_endpoints}/{total_endpoints} working ({endpoint_rate:.1%})")
    
    # Processing summary
    if processing_results.get('processing_successful'):
        fields_rate = processing_results.get('success_rate', 0)
        print(f"⚙️  Content Processing: {processing_results.get('fields_found', 0)}/{processing_results.get('total_fields', 5)} TICKET 3 fields ({fields_rate:.1%})")
    else:
        print(f"⚙️  Content Processing: Failed - {processing_results.get('error', 'Unknown error')}")
    
    # Library summary
    if library_results.get('library_accessible'):
        persistence_rate = library_results.get('persistence_rate', 0)
        print(f"📚 Content Library: {library_results.get('ticket3_articles', 0)}/{library_results.get('checked_articles', 0)} articles with TICKET 3 data ({persistence_rate:.1%})")
    else:
        print(f"📚 Content Library: Not accessible - {library_results.get('error', 'Unknown error')}")
    
    # Overall assessment
    print()
    print("🎯 TICKET 3 IMPLEMENTATION STATUS:")
    
    overall_score = (endpoint_rate + 
                    processing_results.get('success_rate', 0) + 
                    library_results.get('persistence_rate', 0)) / 3
    
    if overall_score >= 0.7:
        print("✅ TICKET 3 implementation is working well!")
        print("   Universal bookmarks and durable links system is functional.")
    elif overall_score >= 0.4:
        print("⚠️  TICKET 3 implementation is partially working.")
        print("   Some components are functional but improvements needed.")
    else:
        print("❌ TICKET 3 implementation needs significant work.")
        print("   Major components are not working as expected.")
    
    print(f"📈 Overall Score: {overall_score:.1%}")
    
    return overall_score >= 0.4

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)