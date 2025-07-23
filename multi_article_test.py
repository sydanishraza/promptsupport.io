#!/usr/bin/env python3
"""
Knowledge Engine Multi-Article Creation Workflow Testing
Testing the enhanced multi-article splitting logic and content generation
"""

import requests
import json
import os
import time
from dotenv import load_dotenv

# Load environment variables
load_dotenv('/app/frontend/.env')

# Get backend URL from environment
BACKEND_URL = os.environ.get('REACT_APP_BACKEND_URL', 'https://3f52be48-ab3d-4f40-b801-4ac8987f855e.preview.emergentagent.com') + '/api'

# Multi-section test content as specified in the review request
MULTI_SECTION_TEST_CONTENT = """# Enterprise Software Documentation

## Chapter 1: System Architecture Overview
This chapter covers the foundational architecture of our enterprise software platform, including core components, data flow patterns, and integration points that form the backbone of the system.

### Core Components
- Authentication Service
- Data Processing Engine  
- User Interface Layer
- Database Management System
- API Gateway

### Integration Patterns
The system uses microservices architecture with event-driven communication patterns.

## Chapter 2: User Management and Authentication
Comprehensive guide to user management, role-based access control, and authentication mechanisms implemented throughout the platform.

### Authentication Methods
- Single Sign-On (SSO)
- Multi-Factor Authentication (MFA)
- OAuth 2.0/OpenID Connect
- LDAP Integration

### Role Management
Define and manage user roles with granular permissions."""

class MultiArticleWorkflowTest:
    def __init__(self):
        self.base_url = BACKEND_URL
        self.test_job_id = None
        print(f"Testing Knowledge Engine Multi-Article Workflow at: {self.base_url}")
        
    def test_multi_article_splitting_logic(self):
        """Test the enhanced should_split_into_multiple_articles function"""
        print("🔍 Testing Multi-Article Splitting Logic...")
        try:
            # Process the multi-section content
            test_content = {
                "content": MULTI_SECTION_TEST_CONTENT,
                "content_type": "text",
                "metadata": {
                    "source": "multi_article_test",
                    "test_type": "splitting_logic_test",
                    "original_filename": "Enterprise_Software_Documentation.md",
                    "file_extension": "md"
                }
            }
            
            print("Processing multi-section content to test splitting logic...")
            response = requests.post(
                f"{self.base_url}/content/process",
                json=test_content,
                timeout=45
            )
            
            print(f"Status Code: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print(f"Response: {json.dumps(data, indent=2)}")
                
                if ("job_id" in data and "status" in data and 
                    "chunks_created" in data and data["chunks_created"] > 0):
                    self.test_job_id = data["job_id"]
                    print(f"✅ Content processing successful - {data['chunks_created']} chunks created")
                    
                    # Wait for processing to complete
                    time.sleep(5)
                    
                    # Check if multiple articles were created in Content Library
                    return self.verify_multiple_articles_created()
                else:
                    print("❌ Content processing failed - invalid response format")
                    return False
            else:
                print(f"❌ Content processing failed - status code {response.status_code}")
                print(f"Response: {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ Multi-article splitting test failed - {str(e)}")
            return False
    
    def verify_multiple_articles_created(self):
        """Verify that multiple articles were created from the multi-section content"""
        print("\n🔍 Verifying Multiple Articles Creation...")
        try:
            # Get Content Library articles
            response = requests.get(f"{self.base_url}/content-library", timeout=10)
            
            if response.status_code != 200:
                print(f"❌ Could not retrieve Content Library - status code {response.status_code}")
                return False
            
            data = response.json()
            articles = data.get('articles', [])
            
            print(f"Total articles in Content Library: {len(articles)}")
            
            # Look for articles created from our test content
            test_articles = []
            for article in articles:
                metadata = article.get('metadata', {})
                if (metadata.get('source') == 'multi_article_test' or 
                    'Enterprise Software Documentation' in article.get('title', '') or
                    'System Architecture' in article.get('title', '') or
                    'User Management' in article.get('title', '')):
                    test_articles.append(article)
            
            print(f"Articles created from test content: {len(test_articles)}")
            
            if len(test_articles) > 1:
                print("✅ Multiple articles created successfully!")
                
                # Verify article structure and content
                for i, article in enumerate(test_articles):
                    print(f"\nArticle {i+1}:")
                    print(f"  Title: {article.get('title', 'N/A')}")
                    print(f"  Summary: {article.get('summary', 'N/A')[:100]}...")
                    print(f"  Tags: {article.get('tags', [])}")
                    print(f"  Content length: {len(article.get('content', ''))}")
                
                return True
            elif len(test_articles) == 1:
                print("⚠️ Only one article created - splitting logic may not have triggered")
                print(f"Single article title: {test_articles[0].get('title', 'N/A')}")
                return False
            else:
                print("❌ No articles found from test content")
                return False
                
        except Exception as e:
            print(f"❌ Article verification failed - {str(e)}")
            return False
    
    def test_text_processing_workflow(self):
        """Test POST /api/content/process endpoint with multi-section content"""
        print("\n🔍 Testing Text Processing Workflow with Multi-Section Content...")
        try:
            # Get initial Content Library count
            initial_response = requests.get(f"{self.base_url}/content-library", timeout=10)
            initial_count = 0
            if initial_response.status_code == 200:
                initial_count = initial_response.json().get('total', 0)
            
            print(f"Initial Content Library articles: {initial_count}")
            
            # Process content with enhanced metadata to trigger multi-article creation
            enhanced_content = {
                "content": MULTI_SECTION_TEST_CONTENT + "\n\n## Chapter 3: Data Management\nComprehensive data management strategies including backup, recovery, and archival processes.\n\n### Backup Strategies\n- Automated daily backups\n- Incremental backup systems\n- Cloud backup integration\n\n### Recovery Procedures\nStep-by-step recovery procedures for various failure scenarios.",
                "content_type": "text",
                "metadata": {
                    "source": "workflow_test",
                    "test_type": "text_processing_workflow",
                    "original_filename": "Enhanced_Enterprise_Documentation.docx",
                    "file_extension": "docx",
                    "document_type": "enterprise_documentation",
                    "chapters": 3,
                    "sections": 6
                }
            }
            
            print("Processing enhanced multi-section content...")
            response = requests.post(
                f"{self.base_url}/content/process",
                json=enhanced_content,
                timeout=60
            )
            
            print(f"Status Code: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print(f"Processing Response: {json.dumps(data, indent=2)}")
                
                # Wait for processing and article creation
                time.sleep(8)
                
                # Check final Content Library count
                final_response = requests.get(f"{self.base_url}/content-library", timeout=10)
                if final_response.status_code == 200:
                    final_data = final_response.json()
                    final_count = final_data.get('total', 0)
                    articles = final_data.get('articles', [])
                    
                    print(f"Final Content Library articles: {final_count}")
                    print(f"Articles created: {final_count - initial_count}")
                    
                    # Look for workflow test articles
                    workflow_articles = [
                        article for article in articles 
                        if article.get('metadata', {}).get('source') == 'workflow_test'
                    ]
                    
                    if len(workflow_articles) > 1:
                        print(f"✅ Text processing workflow created {len(workflow_articles)} articles")
                        return True
                    elif len(workflow_articles) == 1:
                        print("⚠️ Workflow created only 1 article - may not have triggered multi-article logic")
                        return False
                    else:
                        print("❌ No articles created from workflow test")
                        return False
                else:
                    print("❌ Could not verify final Content Library state")
                    return False
            else:
                print(f"❌ Text processing workflow failed - status code {response.status_code}")
                print(f"Response: {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ Text processing workflow test failed - {str(e)}")
            return False
    
    def test_enhanced_content_generation(self):
        """Test that enhanced LLM prompts create comprehensive, well-structured articles"""
        print("\n🔍 Testing Enhanced Content Generation Quality...")
        try:
            # Process content specifically designed to test content enhancement
            test_content = {
                "content": """# Advanced Database Management System

## Introduction
This document covers advanced database management concepts for enterprise applications.

## Performance Optimization
Database performance optimization involves multiple strategies including indexing, query optimization, and resource management.

### Indexing Strategies
- B-tree indexes for range queries
- Hash indexes for equality searches
- Composite indexes for multi-column queries

### Query Optimization
- Execution plan analysis
- Query rewriting techniques
- Statistics maintenance

## Security Implementation
Database security requires comprehensive approach including access control, encryption, and auditing.

### Access Control
- Role-based access control (RBAC)
- Attribute-based access control (ABAC)
- Principle of least privilege

### Encryption
- Data at rest encryption
- Data in transit encryption
- Key management strategies

## Backup and Recovery
Comprehensive backup and recovery strategies ensure data availability and business continuity.

### Backup Types
- Full backups
- Incremental backups
- Differential backups

### Recovery Procedures
- Point-in-time recovery
- Disaster recovery planning
- High availability configurations""",
                "content_type": "text",
                "metadata": {
                    "source": "content_generation_test",
                    "test_type": "enhanced_content_generation",
                    "original_filename": "Advanced_Database_Management.md",
                    "file_extension": "md",
                    "document_type": "technical_documentation"
                }
            }
            
            print("Processing content to test enhanced generation...")
            response = requests.post(
                f"{self.base_url}/content/process",
                json=test_content,
                timeout=60
            )
            
            if response.status_code != 200:
                print(f"❌ Content processing failed - status code {response.status_code}")
                return False
            
            # Wait for processing
            time.sleep(10)
            
            # Get articles and analyze quality
            articles_response = requests.get(f"{self.base_url}/content-library", timeout=10)
            if articles_response.status_code != 200:
                print("❌ Could not retrieve articles for quality analysis")
                return False
            
            articles_data = articles_response.json()
            articles = articles_data.get('articles', [])
            
            # Find our test articles
            test_articles = [
                article for article in articles 
                if article.get('metadata', {}).get('source') == 'content_generation_test'
            ]
            
            if not test_articles:
                print("❌ No articles found from content generation test")
                return False
            
            print(f"Analyzing {len(test_articles)} generated articles...")
            
            quality_score = 0
            total_checks = 0
            
            for i, article in enumerate(test_articles):
                print(f"\n--- Article {i+1} Quality Analysis ---")
                print(f"Title: {article.get('title', 'N/A')}")
                
                # Check title quality
                title = article.get('title', '')
                if len(title) > 10 and not title.startswith('Processed Content'):
                    print("✅ Title: Descriptive and meaningful")
                    quality_score += 1
                else:
                    print("❌ Title: Generic or too short")
                total_checks += 1
                
                # Check summary quality
                summary = article.get('summary', '')
                if len(summary) > 50 and len(summary.split('.')) >= 2:
                    print("✅ Summary: Comprehensive (2+ sentences)")
                    quality_score += 1
                else:
                    print("❌ Summary: Too short or single sentence")
                total_checks += 1
                
                # Check content structure
                content = article.get('content', '')
                if ('##' in content and '###' in content and len(content) > 500):
                    print("✅ Content: Well-structured with multiple heading levels")
                    quality_score += 1
                else:
                    print("❌ Content: Poor structure or too short")
                total_checks += 1
                
                # Check tags quality
                tags = article.get('tags', [])
                if len(tags) >= 3 and any(len(tag) > 3 for tag in tags):
                    print(f"✅ Tags: Comprehensive ({len(tags)} tags)")
                    quality_score += 1
                else:
                    print(f"❌ Tags: Insufficient ({len(tags)} tags)")
                total_checks += 1
                
                # Check for production-ready features
                if ('💡' in content or '⚠️' in content or '**' in content):
                    print("✅ Production Features: Contains callouts/formatting")
                    quality_score += 1
                else:
                    print("❌ Production Features: Missing callouts/formatting")
                total_checks += 1
                
                print(f"Content preview: {content[:200]}...")
            
            quality_percentage = (quality_score / total_checks) * 100 if total_checks > 0 else 0
            print(f"\n📊 Content Generation Quality Score: {quality_score}/{total_checks} ({quality_percentage:.1f}%)")
            
            if quality_percentage >= 70:
                print("✅ Enhanced content generation is working well")
                return True
            else:
                print("❌ Enhanced content generation needs improvement")
                return False
                
        except Exception as e:
            print(f"❌ Enhanced content generation test failed - {str(e)}")
            return False
    
    def test_content_library_integration(self):
        """Debug Content Library integration for multiple articles"""
        print("\n🔍 Testing Content Library Integration for Multiple Articles...")
        try:
            # Get current state
            response = requests.get(f"{self.base_url}/content-library", timeout=10)
            if response.status_code != 200:
                print(f"❌ Content Library endpoint failed - status code {response.status_code}")
                return False
            
            data = response.json()
            articles = data.get('articles', [])
            total = data.get('total', 0)
            
            print(f"Content Library Status:")
            print(f"  Total articles: {total}")
            print(f"  Articles returned: {len(articles)}")
            
            # Analyze article sources and types
            source_analysis = {}
            ai_processed_count = 0
            multi_article_sources = {}
            
            for article in articles:
                # Source analysis
                source = article.get('source_type', 'unknown')
                source_analysis[source] = source_analysis.get(source, 0) + 1
                
                # AI processing analysis
                metadata = article.get('metadata', {})
                if metadata.get('ai_processed'):
                    ai_processed_count += 1
                
                # Multi-article source analysis
                original_source = metadata.get('source', 'unknown')
                if original_source not in multi_article_sources:
                    multi_article_sources[original_source] = []
                multi_article_sources[original_source].append(article.get('title', 'Untitled'))
            
            print(f"\nSource Type Analysis:")
            for source, count in source_analysis.items():
                print(f"  {source}: {count} articles")
            
            print(f"\nAI Processing Analysis:")
            print(f"  AI-processed articles: {ai_processed_count}/{total}")
            print(f"  Non-AI articles: {total - ai_processed_count}/{total}")
            
            print(f"\nMulti-Article Source Analysis:")
            multi_article_count = 0
            for source, titles in multi_article_sources.items():
                if len(titles) > 1:
                    print(f"  {source}: {len(titles)} articles")
                    multi_article_count += len(titles)
                    for title in titles[:3]:  # Show first 3 titles
                        print(f"    - {title}")
                    if len(titles) > 3:
                        print(f"    ... and {len(titles) - 3} more")
            
            print(f"\nMulti-Article Integration Summary:")
            print(f"  Articles from multi-article sources: {multi_article_count}")
            print(f"  Single-source articles: {total - multi_article_count}")
            
            # Check for recent test articles
            test_sources = ['multi_article_test', 'workflow_test', 'content_generation_test']
            recent_test_articles = []
            
            for article in articles:
                metadata = article.get('metadata', {})
                if metadata.get('source') in test_sources:
                    recent_test_articles.append(article)
            
            if recent_test_articles:
                print(f"\nRecent Test Articles Found: {len(recent_test_articles)}")
                for article in recent_test_articles:
                    print(f"  - {article.get('title', 'Untitled')} (source: {article.get('metadata', {}).get('source')})")
                print("✅ Content Library integration is working")
                return True
            else:
                print("\n⚠️ No recent test articles found, but Content Library is functional")
                return total > 0  # Return True if any articles exist
                
        except Exception as e:
            print(f"❌ Content Library integration test failed - {str(e)}")
            return False
    
    def run_multi_article_tests(self):
        """Run all multi-article workflow tests"""
        print("🚀 Starting Knowledge Engine Multi-Article Creation Workflow Testing")
        print("🎯 FOCUS: Multi-Article Splitting Logic and Content Generation")
        print(f"Backend URL: {self.base_url}")
        print("=" * 80)
        
        results = {}
        
        # Test 1: Multi-Article Splitting Logic
        print("\n🎯 TEST 1: MULTI-ARTICLE SPLITTING LOGIC")
        print("=" * 50)
        results['multi_article_splitting'] = self.test_multi_article_splitting_logic()
        
        # Test 2: Text Processing Workflow
        print("\n🎯 TEST 2: TEXT PROCESSING WORKFLOW")
        print("=" * 50)
        results['text_processing_workflow'] = self.test_text_processing_workflow()
        
        # Test 3: Enhanced Content Generation
        print("\n🎯 TEST 3: ENHANCED CONTENT GENERATION")
        print("=" * 50)
        results['enhanced_content_generation'] = self.test_enhanced_content_generation()
        
        # Test 4: Content Library Integration Debug
        print("\n🎯 TEST 4: CONTENT LIBRARY INTEGRATION DEBUG")
        print("=" * 50)
        results['content_library_integration'] = self.test_content_library_integration()
        
        # Summary
        print("\n" + "=" * 80)
        print("📊 MULTI-ARTICLE WORKFLOW TEST RESULTS")
        print("=" * 80)
        
        passed = 0
        total = len(results)
        
        for test_name, result in results.items():
            status = "✅ PASS" if result else "❌ FAIL"
            print(f"{test_name.replace('_', ' ').title()}: {status}")
            if result:
                passed += 1
        
        print(f"\nOverall: {passed}/{total} tests passed")
        
        # Specific assessment
        if results.get('multi_article_splitting') and results.get('enhanced_content_generation'):
            print("🎉 Multi-article creation workflow is working!")
            return True
        elif results.get('content_library_integration'):
            print("⚠️ Content Library works but multi-article logic may need debugging")
            return False
        else:
            print("❌ Multi-article workflow has critical issues")
            return False

if __name__ == "__main__":
    tester = MultiArticleWorkflowTest()
    success = tester.run_multi_article_tests()
    exit(0 if success else 1)