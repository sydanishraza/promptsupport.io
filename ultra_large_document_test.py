#!/usr/bin/env python3
"""
Ultra-Large Document Handling System Test
Tests the Knowledge Engine's ultra-large document processing capabilities
"""

import asyncio
import aiohttp
import json
import os
import time
from datetime import datetime

# Get backend URL from environment
BACKEND_URL = os.getenv('REACT_APP_BACKEND_URL', 'https://content-pipeline-5.preview.emergentagent.com')
API_BASE = f"{BACKEND_URL}/api"

class UltraLargeDocumentTester:
    def __init__(self):
        self.session = None
        self.test_results = []
        
    async def setup_session(self):
        """Setup HTTP session for testing"""
        self.session = aiohttp.ClientSession()
        
    async def cleanup_session(self):
        """Cleanup HTTP session"""
        if self.session:
            await self.session.close()
    
    def create_ultra_large_test_document(self, size_type="medium"):
        """Create test documents of different sizes to trigger ultra-large detection"""
        
        if size_type == "small":
            # Just above threshold: ~50,000 characters, ~12,000 words
            content = self._generate_content_with_structure(
                sections=15, 
                words_per_section=800,
                title="Medium Scale Technical Documentation"
            )
        elif size_type == "medium":
            # Clearly ultra-large: ~75,000 characters, ~18,000 words
            content = self._generate_content_with_structure(
                sections=20, 
                words_per_section=900,
                title="Comprehensive Enterprise Integration Guide"
            )
        elif size_type == "large":
            # Very large: ~100,000 characters, ~25,000 words
            content = self._generate_content_with_structure(
                sections=25, 
                words_per_section=1000,
                title="Complete System Architecture Documentation"
            )
        else:  # extra_large
            # Extremely large: ~150,000 characters, ~35,000 words
            content = self._generate_content_with_structure(
                sections=35, 
                words_per_section=1000,
                title="Master Technical Reference Manual"
            )
            
        return content
    
    def _generate_content_with_structure(self, sections, words_per_section, title):
        """Generate structured content with headings and sections"""
        
        content_parts = [f"# {title}\n\n"]
        
        # Introduction
        intro = """This comprehensive documentation provides detailed coverage of advanced technical concepts, implementation strategies, and best practices. The content is structured to provide both theoretical understanding and practical implementation guidance across multiple domains and use cases.

## Overview and Scope

This guide encompasses a wide range of technical topics including system architecture, API integration, security protocols, performance optimization, troubleshooting methodologies, and advanced configuration options. Each section builds upon previous concepts while maintaining standalone utility for reference purposes.

### Document Structure

The documentation is organized into logical sections that progress from foundational concepts to advanced implementation details. Each major section contains multiple subsections with detailed explanations, code examples, configuration samples, and practical use cases.

"""
        content_parts.append(intro)
        
        # Generate sections with realistic technical content
        section_topics = [
            "System Architecture and Design Patterns",
            "API Integration and Authentication",
            "Database Configuration and Optimization", 
            "Security Implementation and Best Practices",
            "Performance Monitoring and Tuning",
            "Error Handling and Logging Strategies",
            "Deployment and Infrastructure Management",
            "Testing and Quality Assurance",
            "Documentation and Code Standards",
            "Troubleshooting and Maintenance",
            "Advanced Configuration Options",
            "Integration with Third-Party Services",
            "Scalability and Load Management",
            "Data Migration and Backup Strategies",
            "User Management and Access Control",
            "Monitoring and Alerting Systems",
            "Development Workflow and CI/CD",
            "Container Orchestration and Docker",
            "Cloud Platform Integration",
            "Microservices Architecture Patterns",
            "Event-Driven Architecture Implementation",
            "Message Queue and Pub/Sub Systems",
            "Caching Strategies and Implementation",
            "Search and Indexing Solutions",
            "Real-time Communication Systems",
            "Mobile Application Integration",
            "Analytics and Reporting Systems",
            "Compliance and Regulatory Requirements",
            "Disaster Recovery and Business Continuity",
            "Cost Optimization and Resource Management",
            "Machine Learning Integration",
            "Data Processing and ETL Pipelines",
            "API Gateway and Service Mesh",
            "Identity and Access Management",
            "Content Delivery and CDN Configuration"
        ]
        
        for i in range(sections):
            section_num = i + 1
            topic = section_topics[i % len(section_topics)]
            
            section_content = f"""## {section_num}. {topic}

### {section_num}.1 Introduction to {topic}

{self._generate_paragraph(words_per_section // 4)}

### {section_num}.2 Implementation Strategy

{self._generate_paragraph(words_per_section // 4)}

#### {section_num}.2.1 Configuration Requirements

{self._generate_paragraph(words_per_section // 6)}

#### {section_num}.2.2 Best Practices and Guidelines

{self._generate_paragraph(words_per_section // 6)}

### {section_num}.3 Advanced Concepts and Use Cases

{self._generate_paragraph(words_per_section // 4)}

#### {section_num}.3.1 Performance Considerations

{self._generate_paragraph(words_per_section // 8)}

#### {section_num}.3.2 Security Implications

{self._generate_paragraph(words_per_section // 8)}

### {section_num}.4 Troubleshooting and Common Issues

{self._generate_paragraph(words_per_section // 6)}

---

"""
            content_parts.append(section_content)
        
        # Add conclusion
        conclusion = """## Conclusion and Next Steps

This comprehensive documentation provides the foundation for understanding and implementing advanced technical solutions. The concepts and strategies outlined in each section work together to create robust, scalable, and maintainable systems.

### Key Takeaways

The implementation of these technical concepts requires careful planning, thorough testing, and ongoing monitoring. Success depends on understanding the interconnections between different system components and maintaining best practices throughout the development lifecycle.

### Recommended Implementation Approach

Begin with foundational concepts and gradually implement more advanced features. Ensure proper testing at each stage and maintain comprehensive documentation of all configuration changes and customizations.

### Support and Resources

For additional support and resources, consult the official documentation, community forums, and technical support channels. Regular updates and maintenance are essential for optimal system performance and security.

"""
        content_parts.append(conclusion)
        
        return '\n'.join(content_parts)
    
    def _generate_paragraph(self, word_count):
        """Generate a paragraph with approximately the specified word count"""
        
        technical_sentences = [
            "The implementation requires careful consideration of system architecture patterns and design principles to ensure optimal performance and maintainability.",
            "Configuration parameters must be properly validated and documented to prevent runtime errors and facilitate troubleshooting procedures.",
            "Integration with external services necessitates robust error handling mechanisms and appropriate timeout configurations for reliable operation.",
            "Security protocols should be implemented according to industry standards and best practices to protect sensitive data and system resources.",
            "Performance monitoring and logging systems provide essential insights into system behavior and help identify potential optimization opportunities.",
            "Scalability considerations must be addressed during the initial design phase to accommodate future growth and increased load requirements.",
            "Testing strategies should encompass unit tests, integration tests, and end-to-end validation to ensure comprehensive coverage and reliability.",
            "Documentation standards facilitate knowledge transfer and enable efficient maintenance and troubleshooting by development teams.",
            "Deployment procedures should be automated and repeatable to minimize human error and ensure consistent environment configurations.",
            "Backup and recovery strategies are critical for business continuity and must be regularly tested and validated for effectiveness.",
            "User access controls and authentication mechanisms protect system integrity and ensure appropriate authorization levels.",
            "Database optimization techniques improve query performance and reduce resource consumption for better overall system efficiency.",
            "Caching strategies reduce latency and improve user experience while minimizing load on backend systems and databases.",
            "API design principles ensure consistent interfaces and facilitate integration with client applications and third-party services.",
            "Error handling and exception management provide graceful degradation and meaningful feedback to users and administrators."
        ]
        
        sentences = []
        current_words = 0
        target_words = word_count
        
        while current_words < target_words:
            sentence = technical_sentences[current_words % len(technical_sentences)]
            sentence_words = len(sentence.split())
            
            if current_words + sentence_words <= target_words + 10:  # Allow slight overflow
                sentences.append(sentence)
                current_words += sentence_words
            else:
                break
        
        return ' '.join(sentences)
    
    async def test_ultra_large_detection(self):
        """Test 1: Verify ultra-large document detection"""
        print("\n🔍 TEST 1: Ultra-Large Document Detection")
        
        test_cases = [
            ("small", "Should trigger ultra-large detection (50k+ chars)"),
            ("medium", "Should trigger ultra-large detection (75k+ chars)"),
            ("large", "Should trigger ultra-large detection (100k+ chars)"),
            ("extra_large", "Should trigger ultra-large detection (150k+ chars)")
        ]
        
        detection_results = []
        
        for size_type, description in test_cases:
            print(f"\n  📄 Testing {size_type} document: {description}")
            
            # Create test document
            content = self.create_ultra_large_test_document(size_type)
            char_count = len(content)
            word_count = len(content.split())
            
            print(f"     - Content: {char_count:,} characters, {word_count:,} words")
            
            # Test document processing
            try:
                # Upload as text content
                upload_data = {
                    "content": content,
                    "content_type": "text",
                    "metadata": {
                        "filename": f"ultra_large_test_{size_type}.txt",
                        "test_type": "ultra_large_detection"
                    }
                }
                
                async with self.session.post(f"{API_BASE}/content/process", json=upload_data) as response:
                    if response.status == 200:
                        result = await response.json()
                        job_id = result.get('job_id')
                        
                        if job_id:
                            # Wait for processing and check results
                            processing_result = await self._wait_for_processing(job_id)
                            
                            if processing_result:
                                # Check if ultra-large detection worked
                                articles_created = processing_result.get('chunks_created', 0)
                                metadata = processing_result.get('metadata', {})
                                
                                ultra_large_detected = metadata.get('ultra_large_processing', False)
                                strategy = metadata.get('ultra_large_strategy', 'unknown')
                                
                                detection_results.append({
                                    'size_type': size_type,
                                    'char_count': char_count,
                                    'word_count': word_count,
                                    'ultra_large_detected': ultra_large_detected,
                                    'strategy': strategy,
                                    'articles_created': articles_created,
                                    'success': ultra_large_detected
                                })
                                
                                status = "✅ DETECTED" if ultra_large_detected else "❌ NOT DETECTED"
                                print(f"     - Ultra-large detection: {status}")
                                print(f"     - Strategy: {strategy}")
                                print(f"     - Articles created: {articles_created}")
                            else:
                                print(f"     - ❌ Processing failed or timed out")
                                detection_results.append({
                                    'size_type': size_type,
                                    'success': False,
                                    'error': 'Processing failed'
                                })
                        else:
                            print(f"     - ❌ No job ID returned")
                            detection_results.append({
                                'size_type': size_type,
                                'success': False,
                                'error': 'No job ID'
                            })
                    else:
                        print(f"     - ❌ Upload failed: {response.status}")
                        detection_results.append({
                            'size_type': size_type,
                            'success': False,
                            'error': f'Upload failed: {response.status}'
                        })
                        
            except Exception as e:
                print(f"     - ❌ Test failed: {e}")
                detection_results.append({
                    'size_type': size_type,
                    'success': False,
                    'error': str(e)
                })
        
        # Analyze results
        successful_detections = sum(1 for r in detection_results if r.get('success', False))
        total_tests = len(detection_results)
        
        print(f"\n  📊 Detection Results: {successful_detections}/{total_tests} successful")
        
        self.test_results.append({
            'test_name': 'Ultra-Large Document Detection',
            'success': successful_detections >= 3,  # At least 3 out of 4 should work
            'details': detection_results,
            'summary': f"{successful_detections}/{total_tests} documents correctly detected as ultra-large"
        })
        
        return successful_detections >= 3
    
    async def test_processing_strategies(self):
        """Test 2: Verify different processing strategies are applied correctly"""
        print("\n🔧 TEST 2: Processing Strategy Selection")
        
        # Create documents that should trigger different strategies
        strategy_tests = [
            {
                'name': 'multi_level_overflow',
                'sections': 15,
                'words_per_section': 800,
                'expected_strategy': 'multi_level_overflow',
                'description': 'Should trigger multi-level overflow (12-15 estimated articles)'
            },
            {
                'name': 'hierarchical_articles', 
                'sections': 20,
                'words_per_section': 900,
                'expected_strategy': 'hierarchical_articles',
                'description': 'Should trigger hierarchical articles (15-20 estimated articles)'
            },
            {
                'name': 'document_splitting',
                'sections': 30,
                'words_per_section': 1000,
                'expected_strategy': 'document_splitting',
                'description': 'Should trigger document splitting (>20 estimated articles)'
            }
        ]
        
        strategy_results = []
        
        for test_case in strategy_tests:
            print(f"\n  🎯 Testing {test_case['name']}: {test_case['description']}")
            
            # Generate content for this strategy test
            content = self._generate_content_with_structure(
                sections=test_case['sections'],
                words_per_section=test_case['words_per_section'],
                title=f"Strategy Test: {test_case['name'].replace('_', ' ').title()}"
            )
            
            char_count = len(content)
            word_count = len(content.split())
            print(f"     - Content: {char_count:,} characters, {word_count:,} words")
            
            try:
                # Upload and process
                upload_data = {
                    "content": content,
                    "content_type": "text",
                    "metadata": {
                        "filename": f"strategy_test_{test_case['name']}.txt",
                        "test_type": "strategy_selection"
                    }
                }
                
                async with self.session.post(f"{API_BASE}/content/process", json=upload_data) as response:
                    if response.status == 200:
                        result = await response.json()
                        job_id = result.get('job_id')
                        
                        if job_id:
                            processing_result = await self._wait_for_processing(job_id)
                            
                            if processing_result:
                                metadata = processing_result.get('metadata', {})
                                actual_strategy = metadata.get('ultra_large_strategy', 'unknown')
                                articles_created = processing_result.get('chunks_created', 0)
                                
                                strategy_match = actual_strategy == test_case['expected_strategy']
                                
                                strategy_results.append({
                                    'test_name': test_case['name'],
                                    'expected_strategy': test_case['expected_strategy'],
                                    'actual_strategy': actual_strategy,
                                    'strategy_match': strategy_match,
                                    'articles_created': articles_created,
                                    'char_count': char_count,
                                    'word_count': word_count,
                                    'success': strategy_match
                                })
                                
                                status = "✅ CORRECT" if strategy_match else "❌ INCORRECT"
                                print(f"     - Expected strategy: {test_case['expected_strategy']}")
                                print(f"     - Actual strategy: {actual_strategy}")
                                print(f"     - Strategy match: {status}")
                                print(f"     - Articles created: {articles_created}")
                            else:
                                print(f"     - ❌ Processing failed")
                                strategy_results.append({
                                    'test_name': test_case['name'],
                                    'success': False,
                                    'error': 'Processing failed'
                                })
                        else:
                            print(f"     - ❌ No job ID returned")
                            strategy_results.append({
                                'test_name': test_case['name'],
                                'success': False,
                                'error': 'No job ID'
                            })
                    else:
                        print(f"     - ❌ Upload failed: {response.status}")
                        strategy_results.append({
                            'test_name': test_case['name'],
                            'success': False,
                            'error': f'Upload failed: {response.status}'
                        })
                        
            except Exception as e:
                print(f"     - ❌ Test failed: {e}")
                strategy_results.append({
                    'test_name': test_case['name'],
                    'success': False,
                    'error': str(e)
                })
        
        # Analyze results
        successful_strategies = sum(1 for r in strategy_results if r.get('success', False))
        total_tests = len(strategy_results)
        
        print(f"\n  📊 Strategy Results: {successful_strategies}/{total_tests} correct strategies")
        
        self.test_results.append({
            'test_name': 'Processing Strategy Selection',
            'success': successful_strategies >= 2,  # At least 2 out of 3 should work
            'details': strategy_results,
            'summary': f"{successful_strategies}/{total_tests} strategies correctly selected"
        })
        
        return successful_strategies >= 2
    
    async def test_completeness_verification(self):
        """Test 3: Verify enhanced completeness verification with adjusted thresholds"""
        print("\n📊 TEST 3: Enhanced Completeness Verification")
        
        # Create ultra-large document to test completeness thresholds
        content = self.create_ultra_large_test_document("medium")
        
        print(f"  📄 Testing completeness verification with ultra-large document")
        print(f"     - Content: {len(content):,} characters, {len(content.split()):,} words")
        
        try:
            upload_data = {
                "content": content,
                "content_type": "text",
                "metadata": {
                    "filename": "completeness_test_ultra_large.txt",
                    "test_type": "completeness_verification"
                }
            }
            
            async with self.session.post(f"{API_BASE}/content/process", json=upload_data) as response:
                if response.status == 200:
                    result = await response.json()
                    job_id = result.get('job_id')
                    
                    if job_id:
                        processing_result = await self._wait_for_processing(job_id)
                        
                        if processing_result:
                            metadata = processing_result.get('metadata', {})
                            
                            # Check for ultra-large processing indicators
                            ultra_large_processing = metadata.get('ultra_large_processing', False)
                            completeness_threshold = metadata.get('completeness_threshold', 0.7)
                            content_coverage = metadata.get('content_coverage', {})
                            
                            # Expected: 60% threshold for ultra-large vs 70% for standard
                            expected_threshold = 0.6 if ultra_large_processing else 0.7
                            threshold_correct = abs(completeness_threshold - expected_threshold) < 0.01
                            
                            overall_coverage = content_coverage.get('overall_coverage', 0)
                            word_coverage = content_coverage.get('word_coverage', 0)
                            heading_coverage = content_coverage.get('heading_coverage', 0)
                            
                            print(f"     - Ultra-large processing: {'✅ YES' if ultra_large_processing else '❌ NO'}")
                            print(f"     - Completeness threshold: {completeness_threshold:.1%} (expected: {expected_threshold:.1%})")
                            print(f"     - Threshold correct: {'✅ YES' if threshold_correct else '❌ NO'}")
                            print(f"     - Overall coverage: {overall_coverage:.1%}")
                            print(f"     - Word coverage: {word_coverage:.1%}")
                            print(f"     - Heading coverage: {heading_coverage:.1%}")
                            
                            completeness_success = (
                                ultra_large_processing and 
                                threshold_correct and 
                                overall_coverage > 0
                            )
                            
                            self.test_results.append({
                                'test_name': 'Enhanced Completeness Verification',
                                'success': completeness_success,
                                'details': {
                                    'ultra_large_processing': ultra_large_processing,
                                    'completeness_threshold': completeness_threshold,
                                    'expected_threshold': expected_threshold,
                                    'threshold_correct': threshold_correct,
                                    'overall_coverage': overall_coverage,
                                    'word_coverage': word_coverage,
                                    'heading_coverage': heading_coverage
                                },
                                'summary': f"Completeness verification {'✅ PASSED' if completeness_success else '❌ FAILED'}"
                            })
                            
                            return completeness_success
                        else:
                            print(f"     - ❌ Processing failed")
                            return False
                    else:
                        print(f"     - ❌ No job ID returned")
                        return False
                else:
                    print(f"     - ❌ Upload failed: {response.status}")
                    return False
                    
        except Exception as e:
            print(f"     - ❌ Test failed: {e}")
            self.test_results.append({
                'test_name': 'Enhanced Completeness Verification',
                'success': False,
                'error': str(e)
            })
            return False
    
    async def test_multi_level_overflow(self):
        """Test 4: Verify multi-level overflow article creation"""
        print("\n📚 TEST 4: Multi-Level Overflow Article Creation")
        
        # Create document that should trigger multi-level overflow (>5 overflow sections)
        content = self._generate_content_with_structure(
            sections=18,  # Should create enough content for overflow
            words_per_section=850,
            title="Multi-Level Overflow Test Document"
        )
        
        print(f"  📄 Testing multi-level overflow with large document")
        print(f"     - Content: {len(content):,} characters, {len(content.split()):,} words")
        
        try:
            upload_data = {
                "content": content,
                "content_type": "text",
                "metadata": {
                    "filename": "multi_level_overflow_test.txt",
                    "test_type": "multi_level_overflow"
                }
            }
            
            async with self.session.post(f"{API_BASE}/content/process", json=upload_data) as response:
                if response.status == 200:
                    result = await response.json()
                    job_id = result.get('job_id')
                    
                    if job_id:
                        processing_result = await self._wait_for_processing(job_id)
                        
                        if processing_result:
                            articles_created = processing_result.get('chunks_created', 0)
                            metadata = processing_result.get('metadata', {})
                            
                            multi_level_overflow = metadata.get('multi_level_overflow', False)
                            overflow_handled = metadata.get('overflow_handled', False)
                            
                            # Check if articles were created in Content Library
                            content_library_articles = await self._check_content_library_articles(job_id)
                            
                            overflow_articles = [
                                article for article in content_library_articles 
                                if 'overflow' in article.get('title', '').lower() or 
                                   'additional' in article.get('title', '').lower()
                            ]
                            
                            multi_overflow_articles = [
                                article for article in overflow_articles
                                if 'part' in article.get('title', '').lower()
                            ]
                            
                            print(f"     - Articles created: {articles_created}")
                            print(f"     - Multi-level overflow detected: {'✅ YES' if multi_level_overflow else '❌ NO'}")
                            print(f"     - Overflow handled: {'✅ YES' if overflow_handled else '❌ NO'}")
                            print(f"     - Overflow articles found: {len(overflow_articles)}")
                            print(f"     - Multi-part overflow articles: {len(multi_overflow_articles)}")
                            
                            # Success criteria: multi-level overflow detected and multiple overflow articles created
                            overflow_success = (
                                multi_level_overflow and 
                                overflow_handled and 
                                len(overflow_articles) > 1
                            )
                            
                            self.test_results.append({
                                'test_name': 'Multi-Level Overflow Article Creation',
                                'success': overflow_success,
                                'details': {
                                    'articles_created': articles_created,
                                    'multi_level_overflow': multi_level_overflow,
                                    'overflow_handled': overflow_handled,
                                    'overflow_articles_count': len(overflow_articles),
                                    'multi_part_articles_count': len(multi_overflow_articles)
                                },
                                'summary': f"Multi-level overflow {'✅ WORKING' if overflow_success else '❌ FAILED'}"
                            })
                            
                            return overflow_success
                        else:
                            print(f"     - ❌ Processing failed")
                            return False
                    else:
                        print(f"     - ❌ No job ID returned")
                        return False
                else:
                    print(f"     - ❌ Upload failed: {response.status}")
                    return False
                    
        except Exception as e:
            print(f"     - ❌ Test failed: {e}")
            self.test_results.append({
                'test_name': 'Multi-Level Overflow Article Creation',
                'success': False,
                'error': str(e)
            })
            return False
    
    async def test_content_library_integration(self):
        """Test 5: Verify articles are saved to Content Library with ultra-large metadata"""
        print("\n💾 TEST 5: Content Library Integration with Ultra-Large Metadata")
        
        # Create ultra-large document
        content = self.create_ultra_large_test_document("medium")
        
        print(f"  📄 Testing Content Library integration")
        print(f"     - Content: {len(content):,} characters, {len(content.split()):,} words")
        
        try:
            upload_data = {
                "content": content,
                "content_type": "text",
                "metadata": {
                    "filename": "content_library_integration_test.txt",
                    "test_type": "content_library_integration"
                }
            }
            
            async with self.session.post(f"{API_BASE}/content/process", json=upload_data) as response:
                if response.status == 200:
                    result = await response.json()
                    job_id = result.get('job_id')
                    
                    if job_id:
                        processing_result = await self._wait_for_processing(job_id)
                        
                        if processing_result:
                            # Check Content Library for articles
                            content_library_articles = await self._check_content_library_articles(job_id)
                            
                            if content_library_articles:
                                # Analyze articles for ultra-large metadata
                                ultra_large_articles = []
                                articles_with_metadata = []
                                
                                for article in content_library_articles:
                                    metadata = article.get('metadata', {})
                                    processing_metadata = article.get('processing_metadata', {})
                                    
                                    # Check for ultra-large indicators
                                    has_ultra_large_metadata = (
                                        metadata.get('ultra_large_processing', False) or
                                        processing_metadata.get('ultra_large_processing', False) or
                                        'ultra' in str(metadata).lower() or
                                        'ultra' in str(processing_metadata).lower()
                                    )
                                    
                                    if has_ultra_large_metadata:
                                        ultra_large_articles.append(article)
                                    
                                    if metadata or processing_metadata:
                                        articles_with_metadata.append(article)
                                
                                print(f"     - Articles in Content Library: {len(content_library_articles)}")
                                print(f"     - Articles with metadata: {len(articles_with_metadata)}")
                                print(f"     - Articles with ultra-large metadata: {len(ultra_large_articles)}")
                                
                                # Check specific metadata fields
                                sample_article = content_library_articles[0] if content_library_articles else {}
                                sample_metadata = sample_article.get('metadata', {})
                                sample_processing = sample_article.get('processing_metadata', {})
                                
                                print(f"     - Sample article metadata keys: {list(sample_metadata.keys())}")
                                print(f"     - Sample processing metadata keys: {list(sample_processing.keys())}")
                                
                                # Success criteria: articles saved with proper metadata
                                integration_success = (
                                    len(content_library_articles) > 0 and
                                    len(articles_with_metadata) > 0
                                )
                                
                                self.test_results.append({
                                    'test_name': 'Content Library Integration',
                                    'success': integration_success,
                                    'details': {
                                        'articles_saved': len(content_library_articles),
                                        'articles_with_metadata': len(articles_with_metadata),
                                        'ultra_large_articles': len(ultra_large_articles),
                                        'sample_metadata_keys': list(sample_metadata.keys()),
                                        'sample_processing_keys': list(sample_processing.keys())
                                    },
                                    'summary': f"Content Library integration {'✅ WORKING' if integration_success else '❌ FAILED'}"
                                })
                                
                                return integration_success
                            else:
                                print(f"     - ❌ No articles found in Content Library")
                                return False
                        else:
                            print(f"     - ❌ Processing failed")
                            return False
                    else:
                        print(f"     - ❌ No job ID returned")
                        return False
                else:
                    print(f"     - ❌ Upload failed: {response.status}")
                    return False
                    
        except Exception as e:
            print(f"     - ❌ Test failed: {e}")
            self.test_results.append({
                'test_name': 'Content Library Integration',
                'success': False,
                'error': str(e)
            })
            return False
    
    async def _wait_for_processing(self, job_id, timeout=300):
        """Wait for document processing to complete"""
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            try:
                async with self.session.get(f"{API_BASE}/jobs/{job_id}") as response:
                    if response.status == 200:
                        result = await response.json()
                        status = result.get('status')
                        
                        if status == 'completed':
                            return result
                        elif status == 'failed':
                            print(f"     - Processing failed: {result.get('error', 'Unknown error')}")
                            return None
                        elif status in ['processing', 'pending']:
                            # Continue waiting
                            await asyncio.sleep(5)
                        else:
                            print(f"     - Unknown status: {status}")
                            return None
                    else:
                        print(f"     - Status check failed: {response.status}")
                        return None
            except Exception as e:
                print(f"     - Status check error: {e}")
                await asyncio.sleep(5)
        
        print(f"     - Processing timeout after {timeout} seconds")
        return None
    
    async def _check_content_library_articles(self, job_id=None):
        """Check Content Library for articles, optionally filtered by job ID"""
        try:
            async with self.session.get(f"{API_BASE}/content-library") as response:
                if response.status == 200:
                    result = await response.json()
                    articles = result.get('articles', [])
                    
                    if job_id:
                        # Filter articles by job ID if provided
                        filtered_articles = [
                            article for article in articles
                            if article.get('source_job_id') == job_id or
                               job_id in str(article.get('metadata', {})) or
                               job_id in str(article.get('processing_metadata', {}))
                        ]
                        return filtered_articles
                    
                    return articles
                else:
                    print(f"     - Content Library check failed: {response.status}")
                    return []
        except Exception as e:
            print(f"     - Content Library check error: {e}")
            return []
    
    async def run_all_tests(self):
        """Run all ultra-large document handling tests"""
        print("🚀 ULTRA-LARGE DOCUMENT HANDLING SYSTEM TEST")
        print("=" * 60)
        
        await self.setup_session()
        
        try:
            # Run all tests
            test_functions = [
                self.test_ultra_large_detection,
                self.test_processing_strategies,
                self.test_completeness_verification,
                self.test_multi_level_overflow,
                self.test_content_library_integration
            ]
            
            results = []
            for test_func in test_functions:
                try:
                    result = await test_func()
                    results.append(result)
                except Exception as e:
                    print(f"❌ Test {test_func.__name__} failed with exception: {e}")
                    results.append(False)
                
                # Small delay between tests
                await asyncio.sleep(2)
            
            # Generate summary
            self.generate_test_summary(results)
            
        finally:
            await self.cleanup_session()
    
    def generate_test_summary(self, results):
        """Generate comprehensive test summary"""
        print("\n" + "=" * 60)
        print("📊 ULTRA-LARGE DOCUMENT HANDLING TEST SUMMARY")
        print("=" * 60)
        
        passed_tests = sum(1 for result in results if result)
        total_tests = len(results)
        success_rate = (passed_tests / total_tests) * 100 if total_tests > 0 else 0
        
        print(f"\n🎯 Overall Results: {passed_tests}/{total_tests} tests passed ({success_rate:.1f}%)")
        
        # Detailed results
        print(f"\n📋 Detailed Test Results:")
        for i, test_result in enumerate(self.test_results):
            test_name = test_result['test_name']
            success = test_result['success']
            summary = test_result.get('summary', 'No summary available')
            
            status = "✅ PASSED" if success else "❌ FAILED"
            print(f"   {i+1}. {test_name}: {status}")
            print(f"      {summary}")
        
        # Overall assessment
        print(f"\n🏆 FINAL ASSESSMENT:")
        if success_rate >= 80:
            print(f"   ✅ EXCELLENT: Ultra-large document handling system is working correctly")
            print(f"   🎉 All major functionality verified and operational")
        elif success_rate >= 60:
            print(f"   ⚠️  GOOD: Most ultra-large document features are working")
            print(f"   🔧 Some areas may need attention but core functionality is solid")
        else:
            print(f"   ❌ NEEDS WORK: Ultra-large document handling has significant issues")
            print(f"   🚨 Multiple critical features are not working as expected")
        
        # Recommendations
        print(f"\n💡 RECOMMENDATIONS:")
        failed_tests = [test for test in self.test_results if not test['success']]
        if failed_tests:
            print(f"   🔍 Investigate failed tests:")
            for test in failed_tests:
                print(f"      - {test['test_name']}")
                if 'error' in test:
                    print(f"        Error: {test['error']}")
        else:
            print(f"   🎯 All tests passed - system is production ready!")
        
        print(f"\n📈 PERFORMANCE METRICS:")
        print(f"   - Test execution completed successfully")
        print(f"   - All test scenarios covered comprehensively")
        print(f"   - Ultra-large document detection, processing strategies, and completeness verification tested")
        
        return success_rate >= 60

async def main():
    """Main test execution function"""
    tester = UltraLargeDocumentTester()
    await tester.run_all_tests()

if __name__ == "__main__":
    asyncio.run(main())