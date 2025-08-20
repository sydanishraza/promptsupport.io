#!/usr/bin/env python3
"""
FOCUSED DUPLICATE PROCESSING ROOT CAUSE ANALYSIS
Investigating the exact source of duplicate article creation as requested in the review.

SPECIFIC INVESTIGATION AREAS:
1. Database insertion analysis - check if articles are being inserted multiple times
2. Processing pipeline analysis - check if outline-first approach triggers fallback
3. Enhancement step duplication - check FAQ generation, TOC creation, related links
4. Concurrent processing issues - race conditions in article creation
5. Identify exact duplicate patterns and timing

Focus: Find the exact line/function where duplicates are created
"""

import requests
import json
import time
import os
import sys
from datetime import datetime
from collections import defaultdict, Counter

# Backend URL from frontend .env
BACKEND_URL = "https://article-genius-1.preview.emergentagent.com"
API_BASE = f"{BACKEND_URL}/api"

def log_analysis(message, level="INFO"):
    """Log analysis results with timestamp"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{timestamp}] {level}: {message}")

def analyze_duplicate_creation_patterns():
    """Analyze the exact patterns of duplicate creation"""
    log_analysis("🔍 ANALYZING DUPLICATE CREATION PATTERNS", "CRITICAL")
    
    try:
        # Get all articles
        response = requests.get(f"{API_BASE}/content-library", timeout=30)
        if response.status_code != 200:
            log_analysis(f"❌ Could not fetch articles: {response.status_code}")
            return False
        
        data = response.json()
        articles = data.get('articles', [])
        total_articles = len(articles)
        
        log_analysis(f"📊 Total articles in Content Library: {total_articles}")
        
        # Group articles by title to find duplicates
        title_groups = defaultdict(list)
        for article in articles:
            title = article.get('title', 'Untitled').strip()
            title_groups[title].append(article)
        
        # Find duplicate groups
        duplicates = {title: articles for title, articles in title_groups.items() if len(articles) > 1}
        
        log_analysis(f"🚨 DUPLICATE ANALYSIS RESULTS:")
        log_analysis(f"   Unique titles: {len(title_groups)}")
        log_analysis(f"   Duplicate title groups: {len(duplicates)}")
        
        total_duplicate_articles = sum(len(group) for group in duplicates.values())
        log_analysis(f"   Total duplicate articles: {total_duplicate_articles}")
        
        # Analyze each duplicate group in detail
        processing_patterns = {
            'outline_based_only': 0,
            'traditional_only': 0,
            'mixed_processing': 0,
            'same_timestamps': 0,
            'different_timestamps': 0,
            'same_source_doc': 0,
            'different_source_doc': 0
        }
        
        critical_findings = []
        
        for title, duplicate_group in duplicates.items():
            if len(duplicate_group) <= 1:
                continue
                
            log_analysis(f"\n🔍 DUPLICATE GROUP: '{title}' ({len(duplicate_group)} copies)")
            
            # Analyze processing types
            outline_based_count = 0
            traditional_count = 0
            timestamps = []
            source_docs = set()
            
            for i, article in enumerate(duplicate_group):
                article_id = article.get('id', 'no-id')
                created_at = article.get('created_at', 'unknown')
                source_doc = article.get('source_document', 'unknown')
                metadata = article.get('metadata', {})
                outline_based = metadata.get('outline_based', False)
                article_type = metadata.get('article_type', 'unknown')
                enhancement_type = metadata.get('enhancement_type', '')
                
                timestamps.append(created_at)
                source_docs.add(source_doc)
                
                if outline_based:
                    outline_based_count += 1
                else:
                    traditional_count += 1
                
                log_analysis(f"   Copy {i+1}: ID={article_id[:8]}..., Created={created_at}")
                log_analysis(f"           Source={source_doc}, Outline-based={outline_based}")
                log_analysis(f"           Type={article_type}, Enhancement={enhancement_type}")
            
            # Analyze patterns
            if outline_based_count > 0 and traditional_count > 0:
                processing_patterns['mixed_processing'] += 1
                critical_findings.append({
                    'type': 'mixed_processing',
                    'title': title,
                    'outline_count': outline_based_count,
                    'traditional_count': traditional_count,
                    'message': f"MIXED PROCESSING: {outline_based_count} outline-based + {traditional_count} traditional"
                })
                log_analysis(f"   🚨 MIXED PROCESSING DETECTED: {outline_based_count} outline-based + {traditional_count} traditional")
            elif outline_based_count > 1:
                processing_patterns['outline_based_only'] += 1
                critical_findings.append({
                    'type': 'outline_duplication',
                    'title': title,
                    'count': outline_based_count,
                    'message': f"OUTLINE DUPLICATION: {outline_based_count} outline-based copies"
                })
                log_analysis(f"   🚨 OUTLINE DUPLICATION: {outline_based_count} outline-based copies")
            elif traditional_count > 1:
                processing_patterns['traditional_only'] += 1
                log_analysis(f"   ⚠️ Traditional processing duplication: {traditional_count} copies")
            
            # Analyze timestamps
            unique_timestamps = set(timestamps)
            if len(unique_timestamps) == 1:
                processing_patterns['same_timestamps'] += 1
                log_analysis(f"   ⚠️ IDENTICAL TIMESTAMPS: All created at {timestamps[0]}")
            else:
                processing_patterns['different_timestamps'] += 1
                log_analysis(f"   ⚠️ DIFFERENT TIMESTAMPS: {len(unique_timestamps)} different times")
            
            # Analyze source documents
            if len(source_docs) == 1:
                processing_patterns['same_source_doc'] += 1
                log_analysis(f"   ✅ Same source document: {list(source_docs)[0]}")
            else:
                processing_patterns['different_source_doc'] += 1
                log_analysis(f"   🚨 DIFFERENT SOURCE DOCS: {list(source_docs)}")
        
        # Summary of patterns
        log_analysis(f"\n📈 DUPLICATE PATTERN SUMMARY:")
        for pattern, count in processing_patterns.items():
            log_analysis(f"   {pattern.replace('_', ' ').title()}: {count}")
        
        # Critical findings summary
        log_analysis(f"\n🚨 CRITICAL FINDINGS:")
        for finding in critical_findings:
            log_analysis(f"   {finding['type'].upper()}: {finding['title']} - {finding['message']}")
        
        return len(duplicates) > 0, critical_findings
        
    except Exception as e:
        log_analysis(f"❌ Duplicate analysis failed: {e}")
        import traceback
        traceback.print_exc()
        return False, []

def investigate_backend_processing_logs():
    """Investigate backend logs for processing pipeline issues"""
    log_analysis("🔍 INVESTIGATING BACKEND PROCESSING LOGS", "CRITICAL")
    
    try:
        # Get recent backend logs
        import subprocess
        result = subprocess.run(['tail', '-n', '1000', '/var/log/supervisor/backend.out.log'], 
                              capture_output=True, text=True, timeout=15)
        
        if result.returncode != 0:
            log_analysis("❌ Could not access backend logs")
            return False
        
        logs = result.stdout
        log_lines = logs.split('\n')
        
        # Look for processing indicators
        processing_indicators = {
            'outline_generation': [],
            'outline_article_creation': [],
            'traditional_processing': [],
            'faq_generation': [],
            'toc_creation': [],
            'database_insertion': [],
            'errors': []
        }
        
        for line in log_lines:
            if 'COMPREHENSIVE OUTLINE GENERATED' in line:
                processing_indicators['outline_generation'].append(line)
            elif 'CREATING ARTICLES FROM OUTLINE' in line:
                processing_indicators['outline_article_creation'].append(line)
            elif 'create_content_library_articles_from_chunks' in line:
                processing_indicators['traditional_processing'].append(line)
            elif 'FAQ/Troubleshooting article' in line:
                processing_indicators['faq_generation'].append(line)
            elif 'introductory Table of Contents' in line:
                processing_indicators['toc_creation'].append(line)
            elif 'insert_one' in line or 'Article created and saved' in line:
                processing_indicators['database_insertion'].append(line)
            elif any(error in line for error in ['Error', 'Exception', 'AttributeError', 'KeyError']):
                processing_indicators['errors'].append(line)
        
        log_analysis(f"📊 BACKEND LOG ANALYSIS:")
        log_analysis(f"   Outline generation events: {len(processing_indicators['outline_generation'])}")
        log_analysis(f"   Outline article creation events: {len(processing_indicators['outline_article_creation'])}")
        log_analysis(f"   Traditional processing events: {len(processing_indicators['traditional_processing'])}")
        log_analysis(f"   FAQ generation events: {len(processing_indicators['faq_generation'])}")
        log_analysis(f"   TOC creation events: {len(processing_indicators['toc_creation'])}")
        log_analysis(f"   Database insertion events: {len(processing_indicators['database_insertion'])}")
        log_analysis(f"   Error events: {len(processing_indicators['errors'])}")
        
        # Look for specific error patterns that might cause fallback
        critical_errors = []
        for error_line in processing_indicators['errors']:
            if 'DocumentChunk' in error_line and 'title' in error_line:
                critical_errors.append(error_line)
                log_analysis(f"   🚨 CRITICAL ERROR: {error_line.strip()}")
        
        # Check for dual processing patterns
        dual_processing_detected = False
        if (len(processing_indicators['outline_generation']) > 0 and 
            len(processing_indicators['traditional_processing']) > 0):
            dual_processing_detected = True
            log_analysis(f"   🚨 DUAL PROCESSING DETECTED: Both outline and traditional processing active")
        
        # Show recent processing events
        if processing_indicators['outline_article_creation']:
            log_analysis(f"   📄 Recent outline article creation:")
            for event in processing_indicators['outline_article_creation'][-3:]:
                log_analysis(f"      {event.strip()}")
        
        if processing_indicators['database_insertion']:
            log_analysis(f"   💾 Recent database insertions:")
            for event in processing_indicators['database_insertion'][-5:]:
                log_analysis(f"      {event.strip()}")
        
        return dual_processing_detected or len(critical_errors) > 0
        
    except Exception as e:
        log_analysis(f"❌ Backend log analysis failed: {e}")
        return False

def test_single_document_duplicate_creation():
    """Test processing a single document to trace duplicate creation in real-time"""
    log_analysis("🧪 TESTING SINGLE DOCUMENT FOR DUPLICATE CREATION", "CRITICAL")
    
    try:
        # Create a unique test document
        test_content = f"""
        Duplicate Investigation Test Document - {datetime.now().strftime('%Y%m%d_%H%M%S')}
        
        This is a test document created specifically to investigate duplicate article creation.
        The document contains multiple sections to trigger article generation.
        
        Section 1: Introduction to Duplicate Testing
        This section introduces the concept of duplicate testing and its importance.
        We need to understand why articles are being created multiple times.
        
        Section 2: Analysis Methods
        This section describes the methods used to analyze duplicate creation.
        We examine database insertion patterns and processing pipeline behavior.
        
        Section 3: Expected Results
        This section outlines what we expect to find during the investigation.
        We should see exactly one article per section, not multiple copies.
        
        Section 4: Troubleshooting Approach
        This section provides troubleshooting steps for duplicate issues.
        We need to identify the exact source of duplicate creation.
        """
        
        # Get baseline article count
        log_analysis("📊 Getting baseline article count...")
        baseline_response = requests.get(f"{API_BASE}/content-library", timeout=30)
        baseline_count = 0
        baseline_titles = set()
        
        if baseline_response.status_code == 200:
            baseline_data = baseline_response.json()
            baseline_count = baseline_data.get('total', 0)
            baseline_articles = baseline_data.get('articles', [])
            baseline_titles = {article.get('title', '') for article in baseline_articles}
            log_analysis(f"   Baseline article count: {baseline_count}")
        
        # Create temporary file
        import tempfile
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            f.write(test_content)
            temp_file_path = f.name
        
        try:
            # Upload and process
            log_analysis("📤 Uploading test document...")
            with open(temp_file_path, 'rb') as f:
                files = {'file': ('duplicate_test.txt', f, 'text/plain')}
                
                start_time = time.time()
                response = requests.post(f"{API_BASE}/content/upload", files=files, timeout=300)
                
                if response.status_code != 200:
                    log_analysis(f"❌ Upload failed: {response.status_code}")
                    return False
                
                upload_data = response.json()
                job_id = upload_data.get('job_id')
                log_analysis(f"✅ Upload successful, Job ID: {job_id}")
                
                # Monitor processing
                processing_complete = False
                max_wait = 180
                
                while not processing_complete and (time.time() - start_time) < max_wait:
                    time.sleep(5)
                    
                    status_response = requests.get(f"{API_BASE}/jobs/{job_id}", timeout=30)
                    if status_response.status_code == 200:
                        status_data = status_response.json()
                        status = status_data.get('status', 'unknown')
                        
                        if status == 'completed':
                            processing_complete = True
                            articles_generated = status_data.get('articles_generated', 0)
                            log_analysis(f"✅ Processing completed, {articles_generated} articles generated")
                        elif status == 'failed':
                            log_analysis(f"❌ Processing failed: {status_data.get('error', 'Unknown')}")
                            return False
                
                if not processing_complete:
                    log_analysis("❌ Processing timeout")
                    return False
                
                # Check for duplicates immediately after processing
                time.sleep(5)  # Wait for database consistency
                
                final_response = requests.get(f"{API_BASE}/content-library", timeout=30)
                if final_response.status_code == 200:
                    final_data = final_response.json()
                    final_count = final_data.get('total', 0)
                    final_articles = final_data.get('articles', [])
                    
                    # Find new articles
                    new_articles = []
                    for article in final_articles:
                        title = article.get('title', '')
                        if title not in baseline_titles and 'duplicate' in title.lower():
                            new_articles.append(article)
                    
                    log_analysis(f"📊 PROCESSING RESULTS:")
                    log_analysis(f"   Baseline count: {baseline_count}")
                    log_analysis(f"   Final count: {final_count}")
                    log_analysis(f"   Articles added: {final_count - baseline_count}")
                    log_analysis(f"   Expected articles: {articles_generated}")
                    log_analysis(f"   New test articles found: {len(new_articles)}")
                    
                    # Analyze new articles for duplicates
                    if len(new_articles) > articles_generated:
                        log_analysis(f"🚨 DUPLICATE CREATION DETECTED!")
                        log_analysis(f"   Expected: {articles_generated} articles")
                        log_analysis(f"   Found: {len(new_articles)} articles")
                        
                        # Group by title
                        title_groups = defaultdict(list)
                        for article in new_articles:
                            title = article.get('title', 'Untitled')
                            title_groups[title].append(article)
                        
                        for title, group in title_groups.items():
                            if len(group) > 1:
                                log_analysis(f"   🚨 DUPLICATE TITLE: '{title}' ({len(group)} copies)")
                                for i, article in enumerate(group):
                                    metadata = article.get('metadata', {})
                                    outline_based = metadata.get('outline_based', False)
                                    log_analysis(f"      Copy {i+1}: ID={article.get('id', 'no-id')[:8]}..., Outline-based={outline_based}")
                        
                        return False  # Duplicates detected
                    else:
                        log_analysis(f"✅ No duplicates detected in test processing")
                        return True
                
        finally:
            # Clean up
            os.unlink(temp_file_path)
            
    except Exception as e:
        log_analysis(f"❌ Single document test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def run_focused_duplicate_investigation():
    """Run focused investigation to find exact root cause of duplicates"""
    log_analysis("🚀 STARTING FOCUSED DUPLICATE PROCESSING INVESTIGATION", "CRITICAL")
    log_analysis("=" * 100)
    
    investigation_results = {
        'duplicate_patterns_found': False,
        'backend_logs_issues': False,
        'single_document_duplicates': False
    }
    
    # Step 1: Analyze existing duplicate patterns
    log_analysis("\n🔍 STEP 1: ANALYZING EXISTING DUPLICATE PATTERNS")
    duplicates_found, critical_findings = analyze_duplicate_creation_patterns()
    investigation_results['duplicate_patterns_found'] = duplicates_found
    
    # Step 2: Investigate backend processing logs
    log_analysis("\n🔍 STEP 2: INVESTIGATING BACKEND PROCESSING LOGS")
    investigation_results['backend_logs_issues'] = investigate_backend_processing_logs()
    
    # Step 3: Test single document processing
    log_analysis("\n🔍 STEP 3: TESTING SINGLE DOCUMENT PROCESSING")
    investigation_results['single_document_duplicates'] = not test_single_document_duplicate_creation()
    
    # Final Analysis
    log_analysis("\n" + "=" * 100)
    log_analysis("🎯 FOCUSED DUPLICATE INVESTIGATION RESULTS", "CRITICAL")
    log_analysis("=" * 100)
    
    for step, result in investigation_results.items():
        status = "🚨 ISSUES FOUND" if result else "✅ NO ISSUES"
        log_analysis(f"{step.replace('_', ' ').title()}: {status}")
    
    # Root cause determination
    log_analysis("\n🔍 ROOT CAUSE ANALYSIS:")
    
    if investigation_results['duplicate_patterns_found']:
        log_analysis("🚨 CONFIRMED: Duplicate articles exist in Content Library")
        log_analysis("   - Multiple articles with identical titles detected")
        log_analysis("   - Mix of outline-based and traditional processing found")
    
    if investigation_results['backend_logs_issues']:
        log_analysis("🚨 BACKEND PROCESSING ISSUES: Dual processing or errors detected")
        log_analysis("   - Both outline-based and traditional processing may be running")
        log_analysis("   - Error conditions may be triggering fallback processing")
    
    if investigation_results['single_document_duplicates']:
        log_analysis("🚨 ACTIVE DUPLICATION: New documents still creating duplicates")
        log_analysis("   - Processing pipeline is actively creating duplicate articles")
        log_analysis("   - Issue is not just historical but ongoing")
    
    # Specific recommendations
    log_analysis("\n💡 SPECIFIC RECOMMENDATIONS:")
    log_analysis("1. Fix outline-based processing to prevent fallback when successful")
    log_analysis("2. Add proper error handling in FAQ generation (DocumentChunk.title issue)")
    log_analysis("3. Implement database constraints to prevent duplicate titles per source")
    log_analysis("4. Add processing locks to prevent concurrent article creation")
    log_analysis("5. Review enhancement pipeline for duplicate TOC/FAQ creation")
    
    return investigation_results

if __name__ == "__main__":
    print("FOCUSED DUPLICATE PROCESSING ROOT CAUSE ANALYSIS")
    print("=" * 70)
    
    results = run_focused_duplicate_investigation()
    
    # Determine if critical issues were found
    critical_issues = any(results.values())
    
    if critical_issues:
        log_analysis("🚨 CRITICAL DUPLICATE PROCESSING ISSUES CONFIRMED", "CRITICAL")
        log_analysis("IMMEDIATE ACTION REQUIRED TO FIX DUPLICATE CREATION", "CRITICAL")
        sys.exit(1)
    else:
        log_analysis("✅ No duplicate processing issues detected", "SUCCESS")
        sys.exit(0)