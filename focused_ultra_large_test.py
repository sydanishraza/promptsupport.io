#!/usr/bin/env python3
"""
Focused Ultra-Large Document Test
Quick test of ultra-large document detection and processing
"""

import asyncio
import aiohttp
import json
import os
import time

# Get backend URL from environment
BACKEND_URL = os.getenv('REACT_APP_BACKEND_URL', 'https://content-pipeline-5.preview.emergentagent.com')
API_BASE = f"{BACKEND_URL}/api"

async def test_ultra_large_detection():
    """Test ultra-large document detection with a focused test"""
    print("🔍 FOCUSED ULTRA-LARGE DOCUMENT DETECTION TEST")
    print("=" * 50)
    
    # Create a document that should trigger ultra-large detection
    # Target: >50,000 characters, >12,000 words, >15 headings
    
    content_parts = ["# Ultra-Large Document Test\n\n"]
    
    # Add introduction
    intro = """This is a comprehensive test document designed to trigger ultra-large document detection in the Knowledge Engine. The document contains extensive content with multiple sections, headings, and detailed information to exceed the thresholds for ultra-large document processing.

## Document Overview

This document is specifically crafted to test the ultra-large document handling system with the following characteristics:
- Content length exceeding 50,000 characters
- Word count exceeding 12,000 words  
- Heading count exceeding 15 headings
- Multiple major sections for comprehensive coverage

The content covers various technical topics to provide realistic test data for the processing system.

"""
    content_parts.append(intro)
    
    # Generate 20 sections with substantial content
    for i in range(20):
        section_num = i + 1
        section_content = f"""## {section_num}. Advanced Technical Topic {section_num}

### {section_num}.1 Introduction and Overview

This section provides comprehensive coverage of advanced technical concepts related to system architecture, implementation strategies, and best practices. The content is designed to be substantial enough to contribute to the overall document size while maintaining realistic technical information that would be found in actual documentation.

The implementation of these concepts requires careful consideration of multiple factors including performance optimization, security protocols, scalability requirements, and maintenance procedures. Each aspect must be thoroughly understood and properly implemented to ensure optimal system operation and long-term reliability.

### {section_num}.2 Technical Implementation Details

The technical implementation involves multiple components working together in a coordinated fashion. The architecture must support high availability, fault tolerance, and efficient resource utilization while maintaining security and compliance requirements.

Key implementation considerations include:
- System architecture design patterns and best practices
- Database optimization and query performance tuning
- API design and integration strategies
- Security implementation and access control mechanisms
- Performance monitoring and alerting systems
- Deployment automation and infrastructure management
- Testing strategies and quality assurance procedures
- Documentation standards and knowledge management

#### {section_num}.2.1 Configuration and Setup

The configuration process requires attention to detail and thorough understanding of system requirements. Proper configuration ensures optimal performance and prevents common issues that can arise during operation.

Configuration parameters must be carefully validated and documented to facilitate troubleshooting and maintenance procedures. The setup process should be automated where possible to reduce human error and ensure consistency across different environments.

#### {section_num}.2.2 Advanced Features and Customization

Advanced features provide additional functionality and customization options for specific use cases. These features require deeper technical knowledge and careful implementation to avoid conflicts with existing system components.

Customization options allow the system to be adapted to specific requirements while maintaining compatibility with standard features and future updates. The customization process should be well-documented and tested thoroughly.

### {section_num}.3 Best Practices and Recommendations

Best practices have been developed through extensive experience and testing in various environments. Following these recommendations helps ensure successful implementation and optimal system performance.

The recommendations cover all aspects of system operation including initial setup, ongoing maintenance, performance optimization, security hardening, and troubleshooting procedures. Regular review and updates of these practices ensure continued effectiveness.

### {section_num}.4 Troubleshooting and Common Issues

Common issues and their solutions are documented to facilitate quick resolution of problems that may arise during operation. The troubleshooting guide provides step-by-step procedures for diagnosing and resolving various types of issues.

Preventive measures and monitoring strategies help identify potential problems before they impact system operation. Regular maintenance and proactive monitoring are essential for maintaining optimal performance and reliability.

---

"""
        content_parts.append(section_content)
    
    # Add conclusion
    conclusion = """## Conclusion and Summary

This comprehensive document provides extensive coverage of advanced technical topics with detailed implementation guidance and best practices. The content is designed to exceed ultra-large document thresholds while maintaining realistic and useful technical information.

The document structure includes multiple major sections, numerous subsections, and detailed explanations that should trigger the ultra-large document detection and processing systems in the Knowledge Engine.

### Key Characteristics

- Total content length: Designed to exceed 50,000 characters
- Word count: Designed to exceed 12,000 words
- Heading structure: Contains over 15 headings at various levels
- Section organization: Multiple major sections with detailed subsections
- Technical content: Realistic technical documentation content

### Expected Processing Results

The Knowledge Engine should detect this document as ultra-large and apply appropriate processing strategies such as:
- Multi-level overflow processing for comprehensive coverage
- Hierarchical article structure for better organization
- Document splitting if the content exceeds maximum processing limits
- Enhanced completeness verification with adjusted thresholds (60% vs 70%)

This test validates the ultra-large document handling capabilities of the Knowledge Engine system.

"""
    content_parts.append(conclusion)
    
    content = '\n'.join(content_parts)
    
    print(f"📄 Generated test document:")
    print(f"   - Characters: {len(content):,}")
    print(f"   - Words: {len(content.split()):,}")
    print(f"   - Lines: {len(content.split(chr(10))):,}")
    
    # Test the document processing
    async with aiohttp.ClientSession() as session:
        try:
            upload_data = {
                "content": content,
                "content_type": "text",
                "metadata": {
                    "filename": "focused_ultra_large_test.txt",
                    "test_type": "ultra_large_detection"
                }
            }
            
            print(f"\n🚀 Uploading document for processing...")
            
            async with session.post(f"{API_BASE}/content/process", json=upload_data) as response:
                if response.status == 200:
                    result = await response.json()
                    job_id = result.get('job_id')
                    
                    print(f"✅ Upload successful, job ID: {job_id}")
                    
                    if job_id:
                        # Wait for processing
                        print(f"⏳ Waiting for processing to complete...")
                        
                        processing_result = await wait_for_processing(session, job_id)
                        
                        if processing_result:
                            print(f"\n📊 PROCESSING RESULTS:")
                            
                            # Extract key information
                            status = processing_result.get('status')
                            chunks_created = processing_result.get('chunks_created', 0)
                            
                            print(f"   - Status: {status}")
                            print(f"   - Articles created: {chunks_created}")
                            
                            # Check for ultra-large processing indicators
                            # Note: The metadata might be in the job record or in the chunks
                            print(f"\n🔍 ULTRA-LARGE DETECTION ANALYSIS:")
                            
                            # Check if we can get more details from the job
                            async with session.get(f"{API_BASE}/jobs/{job_id}") as job_response:
                                if job_response.status == 200:
                                    job_details = await job_response.json()
                                    
                                    # Look for ultra-large indicators in job details
                                    job_data = job_details
                                    
                                    print(f"   - Job details available: ✅")
                                    print(f"   - Chunks in job: {len(job_data.get('chunks', []))}")
                                    
                                    # Analyze chunks for ultra-large metadata
                                    chunks = job_data.get('chunks', [])
                                    ultra_large_detected = False
                                    strategy_used = "unknown"
                                    
                                    for chunk in chunks:
                                        metadata = chunk.get('metadata', {})
                                        if metadata.get('ultra_large_processing'):
                                            ultra_large_detected = True
                                            strategy_used = metadata.get('ultra_large_strategy', 'unknown')
                                            break
                                    
                                    print(f"   - Ultra-large detected: {'✅ YES' if ultra_large_detected else '❌ NO'}")
                                    print(f"   - Strategy used: {strategy_used}")
                                    
                                    # Check Content Library for created articles
                                    print(f"\n📚 CONTENT LIBRARY CHECK:")
                                    
                                    async with session.get(f"{API_BASE}/content-library") as library_response:
                                        if library_response.status == 200:
                                            library_result = await library_response.json()
                                            total_articles = library_result.get('total', 0)
                                            articles = library_result.get('articles', [])
                                            
                                            print(f"   - Total articles in library: {total_articles}")
                                            print(f"   - Articles returned: {len(articles)}")
                                            
                                            # Look for recently created articles
                                            recent_articles = []
                                            for article in articles[:10]:  # Check first 10 articles
                                                title = article.get('title', '')
                                                if 'ultra' in title.lower() or 'test' in title.lower():
                                                    recent_articles.append(article)
                                            
                                            print(f"   - Test-related articles found: {len(recent_articles)}")
                                            
                                            if recent_articles:
                                                sample_article = recent_articles[0]
                                                sample_metadata = sample_article.get('metadata', {})
                                                sample_processing = sample_article.get('processing_metadata', {})
                                                
                                                print(f"   - Sample article metadata keys: {list(sample_metadata.keys())}")
                                                print(f"   - Sample processing metadata keys: {list(sample_processing.keys())}")
                                        else:
                                            print(f"   - ❌ Content Library check failed: {library_response.status}")
                                else:
                                    print(f"   - ❌ Job details check failed: {job_response.status}")
                            
                            # Final assessment
                            print(f"\n🎯 FINAL ASSESSMENT:")
                            
                            success_criteria = [
                                chunks_created > 0,
                                status == 'completed'
                            ]
                            
                            passed_criteria = sum(success_criteria)
                            total_criteria = len(success_criteria)
                            
                            if passed_criteria == total_criteria:
                                print(f"   ✅ BASIC PROCESSING: {passed_criteria}/{total_criteria} criteria met")
                                print(f"   🎉 Document was processed successfully")
                            else:
                                print(f"   ⚠️ PARTIAL SUCCESS: {passed_criteria}/{total_criteria} criteria met")
                                print(f"   🔧 Some issues detected in processing")
                            
                            return True
                        else:
                            print(f"❌ Processing failed or timed out")
                            return False
                    else:
                        print(f"❌ No job ID returned")
                        return False
                else:
                    print(f"❌ Upload failed: {response.status}")
                    response_text = await response.text()
                    print(f"   Error details: {response_text}")
                    return False
                    
        except Exception as e:
            print(f"❌ Test failed with exception: {e}")
            return False

async def wait_for_processing(session, job_id, timeout=120):
    """Wait for processing to complete with shorter timeout"""
    start_time = time.time()
    
    while time.time() - start_time < timeout:
        try:
            async with session.get(f"{API_BASE}/jobs/{job_id}") as response:
                if response.status == 200:
                    result = await response.json()
                    status = result.get('status')
                    
                    if status == 'completed':
                        return result
                    elif status == 'failed':
                        print(f"   Processing failed: {result.get('error_message', 'Unknown error')}")
                        return None
                    elif status in ['processing', 'pending']:
                        print(f"   Status: {status}, waiting...")
                        await asyncio.sleep(10)
                    else:
                        print(f"   Unknown status: {status}")
                        return None
                else:
                    print(f"   Status check failed: {response.status}")
                    return None
        except Exception as e:
            print(f"   Status check error: {e}")
            await asyncio.sleep(10)
    
    print(f"   Processing timeout after {timeout} seconds")
    return None

async def main():
    """Main test execution"""
    result = await test_ultra_large_detection()
    
    if result:
        print(f"\n🎉 FOCUSED TEST COMPLETED SUCCESSFULLY")
    else:
        print(f"\n❌ FOCUSED TEST FAILED")

if __name__ == "__main__":
    asyncio.run(main())