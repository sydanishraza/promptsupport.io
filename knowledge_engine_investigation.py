#!/usr/bin/env python3
"""
DETAILED KNOWLEDGE ENGINE INVESTIGATION
Check the actual job results and Content Library to understand what's happening
"""

import requests
import json
import time
from datetime import datetime

# Backend URL from frontend .env
BACKEND_URL = "https://content-engine-10.preview.emergentagent.com"
API_BASE = f"{BACKEND_URL}/api"

def log_test_result(message, status="INFO"):
    """Log test results with timestamp"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{timestamp}] {status}: {message}")

def check_job_details(job_id):
    """Check detailed job information"""
    try:
        log_test_result(f"🔍 Checking job details for: {job_id}")
        response = requests.get(f"{API_BASE}/jobs/{job_id}", timeout=30)
        
        if response.status_code == 200:
            job_data = response.json()
            log_test_result("✅ Job details retrieved successfully")
            log_test_result(f"📊 Job Status: {job_data.get('status', 'unknown')}")
            log_test_result(f"📊 Input Type: {job_data.get('input_type', 'unknown')}")
            log_test_result(f"📊 Chunks: {len(job_data.get('chunks', []))}")
            
            # Check if chunks contain articles
            chunks = job_data.get('chunks', [])
            total_articles = 0
            for i, chunk in enumerate(chunks):
                articles_in_chunk = len(chunk.get('articles', []))
                total_articles += articles_in_chunk
                log_test_result(f"   Chunk {i+1}: {articles_in_chunk} articles")
            
            log_test_result(f"📊 Total Articles in Job: {total_articles}")
            return job_data
        else:
            log_test_result(f"❌ Could not get job details: Status {response.status_code}")
            return None
            
    except Exception as e:
        log_test_result(f"❌ Error checking job details: {e}")
        return None

def check_recent_content_library_articles():
    """Check recent articles in Content Library"""
    try:
        log_test_result("📚 Checking recent Content Library articles...")
        response = requests.get(f"{API_BASE}/content-library?limit=10", timeout=30)
        
        if response.status_code == 200:
            data = response.json()
            articles = data.get('articles', [])
            total = data.get('total', 0)
            
            log_test_result(f"✅ Content Library: {total} total articles")
            log_test_result("📄 Recent articles:")
            
            for i, article in enumerate(articles[:5]):
                title = article.get('title', 'Untitled')[:50]
                created_at = article.get('created_at', 'unknown')
                source = article.get('source_document', 'unknown')
                log_test_result(f"   {i+1}. {title}... (created: {created_at}, source: {source})")
            
            return articles
        else:
            log_test_result(f"❌ Could not get Content Library: Status {response.status_code}")
            return []
            
    except Exception as e:
        log_test_result(f"❌ Error checking Content Library: {e}")
        return []

def test_with_smaller_content():
    """Test with smaller content to see if processing works"""
    try:
        log_test_result("🧪 Testing with smaller content...")
        
        small_content = """
Customer Summary Screen User Guide - Test Document

This is a comprehensive test document to verify that the Knowledge Engine can process content and generate multiple articles without hard limits.

Chapter 1: Introduction
The Customer Summary Screen is a powerful dashboard that provides unified customer information. This system consolidates data from multiple sources to present a complete view of customer relationships.

Chapter 2: Getting Started
Before using the Customer Summary Screen, users need to understand the basic navigation and setup requirements. The system requires modern browsers and proper authentication.

Chapter 3: Navigation Overview
The interface features an intuitive layout with header navigation, sidebar filters, central dashboard, and detailed information panels. All components work together for efficient workflow.

Chapter 4: Customer Management
Customer profile management allows maintaining detailed records with contact information, account status, communication history, and custom fields for organization-specific data.

Chapter 5: Account Information
The account display shows comprehensive financial information including current balances, payment status, billing history, and subscription details in real-time.

Chapter 6: Transaction Tracking
Transaction history provides detailed records of all customer interactions, purchases, and financial activities with advanced search and filtering capabilities.

Chapter 7: Advanced Features
Advanced functionality includes reporting, analytics, data export, security controls, and integration with external systems for comprehensive customer management.

This document should generate multiple articles to test the hard limit removal functionality.
"""
        
        payload = {
            "content": small_content,
            "content_type": "text",
            "metadata": {
                "original_filename": "Customer Summary Test Guide.txt",
                "source": "test",
                "content_length": len(small_content)
            }
        }
        
        log_test_result(f"📝 Processing {len(small_content)} characters of test content...")
        response = requests.post(f"{API_BASE}/content/process", json=payload, timeout=120)
        
        if response.status_code == 200:
            result = response.json()
            job_id = result.get('job_id')
            chunks_created = result.get('chunks_created', 0)
            
            log_test_result("✅ Small content processing successful")
            log_test_result(f"📊 Job ID: {job_id}")
            log_test_result(f"📊 Chunks Created: {chunks_created}")
            
            # Wait a moment and check job details
            time.sleep(3)
            job_details = check_job_details(job_id)
            
            return True
        else:
            log_test_result(f"❌ Small content processing failed: Status {response.status_code}")
            log_test_result(f"Response: {response.text}")
            return False
            
    except Exception as e:
        log_test_result(f"❌ Small content test failed: {e}")
        return False

def run_investigation():
    """Run detailed investigation"""
    log_test_result("=" * 80)
    log_test_result("KNOWLEDGE ENGINE DETAILED INVESTIGATION", "CRITICAL")
    log_test_result("=" * 80)
    
    # Check current Content Library state
    check_recent_content_library_articles()
    
    # Test with smaller content
    log_test_result("\n🧪 TESTING WITH SMALLER CONTENT")
    test_with_smaller_content()
    
    # Check Content Library again
    log_test_result("\n📚 CHECKING CONTENT LIBRARY AFTER TEST")
    check_recent_content_library_articles()

if __name__ == "__main__":
    run_investigation()