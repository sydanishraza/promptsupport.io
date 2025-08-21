#!/usr/bin/env python3
"""
V2 Engine Step 6 Per-Article Outline Testing
Testing V2PerArticleOutlinePlanner implementation for detailed per-article outline creation
"""

import asyncio
import json
import uuid
from datetime import datetime
from typing import Dict, Any, List
import requests
import sys
import os

# Add backend directory to path for imports
sys.path.append('/app/backend')

# Test configuration
BACKEND_URL = "https://None.preview.emergentagent.com/api"

class V2Step6PerArticleOutlineTest:
    def __init__(self):
        self.test_results = []
        self.backend_url = BACKEND_URL
        
    def log_test(self, test_name: str, success: bool, details: str):
        """Log test results"""
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} {test_name}: {details}")
        self.test_results.append({
            "test": test_name,
            "success": success,
            "details": details
        })
    
    async def test_v2_per_article_outline_planner_instantiation(self):
        """Test V2PerArticleOutlinePlanner class instantiation and configuration"""
        try:
            # Import the class from backend
            from server import V2PerArticleOutlinePlanner
            
            # Test instantiation
            planner = V2PerArticleOutlinePlanner()
            
            # Verify configuration
            assert hasattr(planner, 'min_sections'), "Missing min_sections attribute"
            assert hasattr(planner, 'max_sections'), "Missing max_sections attribute"
            assert hasattr(planner, 'min_faqs'), "Missing min_faqs attribute"
            
            assert planner.min_sections == 3, f"Expected min_sections=3, got {planner.min_sections}"
            assert planner.max_sections == 7, f"Expected max_sections=7, got {planner.max_sections}"
            assert planner.min_faqs == 3, f"Expected min_faqs=3, got {planner.min_faqs}"
            
            # Test method existence
            assert hasattr(planner, 'create_per_article_outlines'), "Missing create_per_article_outlines method"
            assert hasattr(planner, '_create_detailed_article_outline'), "Missing _create_detailed_article_outline method"
            assert hasattr(planner, '_create_blocks_for_article_preview'), "Missing _create_blocks_for_article_preview method"
            assert hasattr(planner, '_perform_llm_article_outline'), "Missing _perform_llm_article_outline method"
            
            self.log_test("V2PerArticleOutlinePlanner Instantiation", True, 
                         f"Class instantiated with correct config: min_sections={planner.min_sections}, max_sections={planner.max_sections}, min_faqs={planner.min_faqs}")
            return True
            
        except Exception as e:
            self.log_test("V2PerArticleOutlinePlanner Instantiation", False, f"Error: {e}")
            return False
    
    async def test_create_per_article_outlines_function(self):
        """Test create_per_article_outlines() function with sample data"""
        try:
            from server import V2PerArticleOutlinePlanner, ContentBlock
            
            planner = V2PerArticleOutlinePlanner()
            
            # Create mock normalized document
            class MockNormalizedDoc:
                def __init__(self):
                    self.doc_id = "test_doc_123"
                    self.blocks = [
                        ContentBlock(
                            block_id="block_1",
                            block_type="heading",
                            content="Introduction to API Testing",
                            level=1
                        ),
                        ContentBlock(
                            block_id="block_2", 
                            block_type="paragraph",
                            content="API testing is essential for ensuring your applications work correctly."
                        ),
                        ContentBlock(
                            block_id="block_3",
                            block_type="code",
                            content="GET /api/test\nContent-Type: application/json",
                            language="http"
                        ),
                        ContentBlock(
                            block_id="block_4",
                            block_type="heading",
                            content="Best Practices",
                            level=2
                        ),
                        ContentBlock(
                            block_id="block_5",
                            block_type="paragraph",
                            content="Follow these best practices for effective API testing."
                        )
                    ]
            
            normalized_doc = MockNormalizedDoc()
            
            # Create sample global outline
            global_outline = {
                "articles": [
                    {
                        "article_id": "article_1",
                        "proposed_title": "API Testing Complete Guide",
                        "block_ids": ["block_1", "block_2", "block_3", "block_4", "block_5"]
                    }
                ]
            }
            
            # Create sample analysis
            analysis = {
                "content_type": "tutorial",
                "audience": "developer",
                "complexity": "intermediate"
            }
            
            run_id = str(uuid.uuid4())
            
            # Test the function
            result = await planner.create_per_article_outlines(
                normalized_doc, global_outline, analysis, run_id
            )
            
            # Verify result structure
            assert isinstance(result, dict), "Result should be a dictionary"
            assert 'per_article_outlines' in result, "Missing per_article_outlines in result"
            assert 'run_id' in result, "Missing run_id in result"
            assert 'doc_id' in result, "Missing doc_id in result"
            
            per_article_outlines = result['per_article_outlines']
            assert isinstance(per_article_outlines, list), "per_article_outlines should be a list"
            assert len(per_article_outlines) > 0, "Should have at least one per-article outline"
            
            # Verify outline structure
            outline = per_article_outlines[0]
            assert 'article_id' in outline, "Missing article_id in outline"
            assert 'outline' in outline, "Missing outline in outline"
            
            self.log_test("create_per_article_outlines Function", True,
                         f"Successfully created {len(per_article_outlines)} per-article outlines for run {run_id}")
            return True
            
        except Exception as e:
            self.log_test("create_per_article_outlines Function", False, f"Error: {e}")
            return False
    
    async def test_create_detailed_article_outline(self):
        """Test _create_detailed_article_outline for individual article outline creation"""
        try:
            from server import V2PerArticleOutlinePlanner, ContentBlock
            
            planner = V2PerArticleOutlinePlanner()
            
            # Create mock normalized document with more comprehensive content
            class MockNormalizedDoc:
                def __init__(self):
                    self.doc_id = "test_doc_456"
                    self.blocks = [
                        ContentBlock(
                            block_id="block_1",
                            block_type="heading",
                            content="Getting Started with REST APIs",
                            level=1
                        ),
                        ContentBlock(
                            block_id="block_2",
                            block_type="paragraph", 
                            content="REST APIs are the backbone of modern web applications. This guide covers everything you need to know."
                        ),
                        ContentBlock(
                            block_id="block_3",
                            block_type="heading",
                            content="Authentication Methods",
                            level=2
                        ),
                        ContentBlock(
                            block_id="block_4",
                            block_type="paragraph",
                            content="There are several authentication methods available for REST APIs including API keys, OAuth, and JWT tokens."
                        ),
                        ContentBlock(
                            block_id="block_5",
                            block_type="code",
                            content="curl -H 'Authorization: Bearer YOUR_TOKEN' https://api.example.com/data",
                            language="bash"
                        ),
                        ContentBlock(
                            block_id="block_6",
                            block_type="heading",
                            content="Error Handling",
                            level=2
                        ),
                        ContentBlock(
                            block_id="block_7",
                            block_type="paragraph",
                            content="Proper error handling is crucial for robust API implementations."
                        )
                    ]
            
            normalized_doc = MockNormalizedDoc()
            
            # Test parameters
            article_id = "article_test_1"
            title = "REST API Complete Guide"
            block_ids = ["block_1", "block_2", "block_3", "block_4", "block_5", "block_6", "block_7"]
            analysis = {
                "content_type": "tutorial",
                "audience": "developer",
                "complexity": "intermediate"
            }
            
            # Test the method
            detailed_outline = await planner._create_detailed_article_outline(
                normalized_doc, article_id, title, block_ids, analysis
            )
            
            # Verify result
            if detailed_outline:
                assert isinstance(detailed_outline, dict), "Detailed outline should be a dictionary"
                
                # Check for required fields
                required_fields = ['title', 'sections', 'faq_suggestions', 'related_link_suggestions']
                for field in required_fields:
                    assert field in detailed_outline, f"Missing required field: {field}"
                
                # Verify sections structure
                sections = detailed_outline['sections']
                assert isinstance(sections, list), "Sections should be a list"
                assert len(sections) >= planner.min_sections, f"Should have at least {planner.min_sections} sections"
                assert len(sections) <= planner.max_sections, f"Should have at most {planner.max_sections} sections"
                
                # Verify FAQ structure
                faqs = detailed_outline['faq_suggestions']
                assert isinstance(faqs, list), "FAQ suggestions should be a list"
                assert len(faqs) >= planner.min_faqs, f"Should have at least {planner.min_faqs} FAQs"
                
                # Verify related links structure
                related_links = detailed_outline['related_link_suggestions']
                assert isinstance(related_links, list), "Related link suggestions should be a list"
                
                self.log_test("_create_detailed_article_outline", True,
                             f"Created detailed outline with {len(sections)} sections, {len(faqs)} FAQs, {len(related_links)} related links")
                return True
            else:
                self.log_test("_create_detailed_article_outline", False, "Method returned None")
                return False
                
        except Exception as e:
            self.log_test("_create_detailed_article_outline", False, f"Error: {e}")
            return False
    
    async def test_create_blocks_for_article_preview(self):
        """Test _create_blocks_for_article_preview generates proper block details for LLM"""
        try:
            from server import V2PerArticleOutlinePlanner, ContentBlock
            
            planner = V2PerArticleOutlinePlanner()
            
            # Create sample article blocks
            article_blocks = [
                {
                    "block_id": "block_1",
                    "block": ContentBlock(
                        block_id="block_1",
                        block_type="heading",
                        content="API Security Best Practices",
                        level=1
                    )
                },
                {
                    "block_id": "block_2", 
                    "block": ContentBlock(
                        block_id="block_2",
                        block_type="paragraph",
                        content="Security is paramount when designing and implementing APIs. This section covers essential security practices."
                    )
                },
                {
                    "block_id": "block_3",
                    "block": ContentBlock(
                        block_id="block_3",
                        block_type="code",
                        content="const jwt = require('jsonwebtoken');\nconst token = jwt.sign({ userId: user.id }, process.env.JWT_SECRET);",
                        language="javascript"
                    )
                }
            ]
            
            title = "API Security Guide"
            analysis = {
                "content_type": "tutorial",
                "audience": "developer",
                "complexity": "advanced"
            }
            
            # Test the method
            preview = planner._create_blocks_for_article_preview(article_blocks, title, analysis)
            
            # Verify preview content
            assert isinstance(preview, str), "Preview should be a string"
            assert len(preview) > 0, "Preview should not be empty"
            
            # Check for required elements
            required_elements = [
                "ARTICLE_TITLE:",
                "TOTAL_BLOCKS:",
                "CONTENT_TYPE:",
                "AUDIENCE:",
                "BLOCKS_FOR_ARTICLE",
                "STRUCTURE_ANALYSIS:"
            ]
            
            for element in required_elements:
                assert element in preview, f"Missing required element: {element}"
            
            # Verify block information is included
            assert "block_1" in preview, "Block ID should be in preview"
            assert "heading" in preview, "Block type should be in preview"
            assert "API Security Best Practices" in preview, "Block content should be in preview"
            assert "javascript" in preview, "Code language should be in preview"
            
            # Verify structure analysis
            assert "Block Types:" in preview, "Block types analysis should be included"
            assert "Heading Levels:" in preview, "Heading levels analysis should be included"
            
            self.log_test("_create_blocks_for_article_preview", True,
                         f"Generated comprehensive preview with {len(article_blocks)} blocks and all required elements")
            return True
            
        except Exception as e:
            self.log_test("_create_blocks_for_article_preview", False, f"Error: {e}")
            return False
    
    async def test_block_allocation_verification(self):
        """Test that ALL assigned block_ids from global outline are used in sections/subsections"""
        try:
            from server import V2PerArticleOutlinePlanner, ContentBlock
            
            planner = V2PerArticleOutlinePlanner()
            
            # Create comprehensive test data
            class MockNormalizedDoc:
                def __init__(self):
                    self.doc_id = "block_allocation_test"
                    self.blocks = [
                        ContentBlock(block_id="block_1", block_type="heading", content="Introduction", level=1),
                        ContentBlock(block_id="block_2", block_type="paragraph", content="Overview paragraph"),
                        ContentBlock(block_id="block_3", block_type="heading", content="Setup", level=2),
                        ContentBlock(block_id="block_4", block_type="paragraph", content="Setup instructions"),
                        ContentBlock(block_id="block_5", block_type="code", content="npm install", language="bash"),
                        ContentBlock(block_id="block_6", block_type="heading", content="Configuration", level=2),
                        ContentBlock(block_id="block_7", block_type="paragraph", content="Configuration details"),
                        ContentBlock(block_id="block_8", block_type="list", content="• Item 1\n• Item 2\n• Item 3")
                    ]
            
            normalized_doc = MockNormalizedDoc()
            
            # Define all block IDs that should be allocated
            all_block_ids = ["block_1", "block_2", "block_3", "block_4", "block_5", "block_6", "block_7", "block_8"]
            
            global_outline = {
                "articles": [
                    {
                        "article_id": "allocation_test_article",
                        "proposed_title": "Complete Setup Guide",
                        "block_ids": all_block_ids
                    }
                ]
            }
            
            analysis = {"content_type": "tutorial", "audience": "developer"}
            run_id = str(uuid.uuid4())
            
            # Create per-article outlines
            result = await planner.create_per_article_outlines(
                normalized_doc, global_outline, analysis, run_id
            )
            
            # Verify block allocation
            per_article_outlines = result.get('per_article_outlines', [])
            assert len(per_article_outlines) > 0, "Should have at least one outline"
            
            outline_data = per_article_outlines[0]['outline']
            
            # Collect all block IDs used in sections/subsections
            used_block_ids = set()
            sections = outline_data.get('sections', [])
            
            for section in sections:
                subsections = section.get('subsections', [])
                for subsection in subsections:
                    block_ids_in_subsection = subsection.get('block_ids', [])
                    used_block_ids.update(block_ids_in_subsection)
            
            # Verify 100% block coverage
            assigned_block_ids = set(all_block_ids)
            missing_blocks = assigned_block_ids - used_block_ids
            extra_blocks = used_block_ids - assigned_block_ids
            
            assert len(missing_blocks) == 0, f"Missing blocks not allocated: {missing_blocks}"
            assert len(extra_blocks) == 0, f"Extra blocks not in original assignment: {extra_blocks}"
            
            # Check validation metadata
            validation_metadata = outline_data.get('validation_metadata', {})
            coverage_percentage = validation_metadata.get('coverage_percentage', 0)
            assert coverage_percentage == 100.0, f"Expected 100% coverage, got {coverage_percentage}%"
            
            self.log_test("Block Allocation Verification", True,
                         f"100% block coverage achieved: {len(used_block_ids)}/{len(assigned_block_ids)} blocks allocated")
            return True
            
        except Exception as e:
            self.log_test("Block Allocation Verification", False, f"Error: {e}")
            return False
    
    async def test_section_structure_creation(self):
        """Test creation of 3-7 main sections with proper organization"""
        try:
            from server import V2PerArticleOutlinePlanner, ContentBlock
            
            planner = V2PerArticleOutlinePlanner()
            
            # Test with different content sizes to verify section count logic
            test_cases = [
                {
                    "name": "Small Content (3 sections)",
                    "blocks": [
                        ContentBlock(block_id="block_1", block_type="heading", content="Introduction", level=1),
                        ContentBlock(block_id="block_2", block_type="paragraph", content="Intro content"),
                        ContentBlock(block_id="block_3", block_type="heading", content="Main Content", level=1),
                        ContentBlock(block_id="block_4", block_type="paragraph", content="Main content")
                    ]
                },
                {
                    "name": "Large Content (7 sections)",
                    "blocks": [
                        ContentBlock(block_id=f"block_{i}", 
                                   block_type="heading" if i % 3 == 1 else "paragraph",
                                   content=f"Content {i}",
                                   level=1 if i % 3 == 1 else None)
                        for i in range(1, 22)  # 21 blocks should create more sections
                    ]
                }
            ]
            
            for test_case in test_cases:
                class MockNormalizedDoc:
                    def __init__(self, blocks):
                        self.doc_id = "section_test"
                        self.blocks = blocks
                
                normalized_doc = MockNormalizedDoc(test_case["blocks"])
                block_ids = [f"block_{i}" for i in range(1, len(test_case["blocks"]) + 1)]
                
                # Test rule-based outline (more predictable)
                outline = await planner._rule_based_article_outline(
                    [{"block_id": bid, "block": block} for bid, block in zip(block_ids, test_case["blocks"])],
                    test_case["name"],
                    block_ids
                )
                
                # Verify section count
                sections = outline.get('sections', [])
                sections_count = len(sections)
                
                assert sections_count >= planner.min_sections, f"Should have at least {planner.min_sections} sections, got {sections_count}"
                assert sections_count <= planner.max_sections, f"Should have at most {planner.max_sections} sections, got {sections_count}"
                
                # Verify section structure
                for section in sections:
                    assert 'heading' in section, "Each section should have a heading"
                    assert 'subsections' in section, "Each section should have subsections"
                    assert isinstance(section['subsections'], list), "Subsections should be a list"
                    
                    # Verify subsection structure
                    for subsection in section['subsections']:
                        assert 'heading' in subsection, "Each subsection should have a heading"
                        assert 'block_ids' in subsection, "Each subsection should have block_ids"
                        assert isinstance(subsection['block_ids'], list), "block_ids should be a list"
                
                # Verify balanced content distribution
                total_blocks_in_sections = sum(
                    len(subsection['block_ids']) 
                    for section in sections 
                    for subsection in section['subsections']
                )
                
                assert total_blocks_in_sections > 0, "Sections should contain blocks"
                
                self.log_test(f"Section Structure - {test_case['name']}", True,
                             f"Created {sections_count} sections with proper structure and {total_blocks_in_sections} total blocks")
            
            return True
            
        except Exception as e:
            self.log_test("Section Structure Creation", False, f"Error: {e}")
            return False
    
    async def test_enhanced_content_features(self):
        """Test FAQ generation and related link suggestions"""
        try:
            from server import V2PerArticleOutlinePlanner, ContentBlock
            
            planner = V2PerArticleOutlinePlanner()
            
            # Create content-rich blocks for FAQ generation
            article_blocks = [
                {
                    "block_id": "block_1",
                    "block": ContentBlock(
                        block_id="block_1",
                        block_type="heading",
                        content="Database Connection Setup",
                        level=1
                    )
                },
                {
                    "block_id": "block_2",
                    "block": ContentBlock(
                        block_id="block_2",
                        block_type="paragraph",
                        content="Setting up database connections requires proper configuration of connection strings, authentication, and connection pooling."
                    )
                },
                {
                    "block_id": "block_3",
                    "block": ContentBlock(
                        block_id="block_3",
                        block_type="code",
                        content="const mongoose = require('mongoose');\nmongoose.connect('mongodb://localhost:27017/myapp');",
                        language="javascript"
                    )
                },
                {
                    "block_id": "block_4",
                    "block": ContentBlock(
                        block_id="block_4",
                        block_type="paragraph",
                        content="Common issues include connection timeouts, authentication failures, and network connectivity problems. For more information, visit https://docs.mongodb.com/manual/reference/connection-string/"
                    )
                }
            ]
            
            # Test rule-based outline generation (more predictable for testing)
            outline = await planner._rule_based_article_outline(
                article_blocks,
                "Database Setup Guide",
                ["block_1", "block_2", "block_3", "block_4"]
            )
            
            # Verify FAQ generation
            faqs = outline.get('faq_suggestions', [])
            assert isinstance(faqs, list), "FAQ suggestions should be a list"
            assert len(faqs) >= planner.min_faqs, f"Should have at least {planner.min_faqs} FAQs, got {len(faqs)}"
            
            # Verify FAQ structure
            for faq in faqs:
                assert 'q' in faq, "Each FAQ should have a question"
                assert 'a' in faq, "Each FAQ should have an answer"
                assert isinstance(faq['q'], str), "Question should be a string"
                assert isinstance(faq['a'], str), "Answer should be a string"
                assert len(faq['q']) > 0, "Question should not be empty"
                assert len(faq['a']) > 0, "Answer should not be empty"
            
            # Verify related links structure
            related_links = outline.get('related_link_suggestions', [])
            assert isinstance(related_links, list), "Related link suggestions should be a list"
            
            # For rule-based outline, related links might be empty, which is acceptable
            for link in related_links:
                assert 'label' in link, "Each link should have a label"
                assert 'url' in link, "Each link should have a URL"
                assert isinstance(link['label'], str), "Label should be a string"
                assert isinstance(link['url'], str), "URL should be a string"
            
            # Test validation metadata
            validation_metadata = outline.get('validation_metadata', {})
            assert 'faqs_count' in validation_metadata, "Should have FAQ count in metadata"
            assert validation_metadata['faqs_count'] == len(faqs), "FAQ count should match actual FAQs"
            
            self.log_test("Enhanced Content Features", True,
                         f"Generated {len(faqs)} FAQs and {len(related_links)} related links with proper structure")
            return True
            
        except Exception as e:
            self.log_test("Enhanced Content Features", False, f"Error: {e}")
            return False
    
    async def test_database_integration(self):
        """Test per-article outline storage and retrieval"""
        try:
            # Test database connectivity first
            health_response = requests.get(f"{self.backend_url}/engine", timeout=10)
            assert health_response.status_code == 200, f"Backend not accessible: {health_response.status_code}"
            
            health_data = health_response.json()
            assert health_data.get('engine') == 'v2', "V2 Engine should be active"
            
            # Test with actual backend processing to verify database integration
            test_content = """# API Testing Guide

## Introduction
API testing is crucial for ensuring your applications work correctly. This comprehensive guide covers all aspects of API testing.

## Authentication Methods
There are several authentication methods available:
- API Keys
- OAuth 2.0
- JWT Tokens

## Testing Strategies
Effective API testing requires a systematic approach:

1. Unit testing individual endpoints
2. Integration testing for workflows
3. Load testing for performance
4. Security testing for vulnerabilities

## Best Practices
Follow these best practices for effective API testing:
- Use automated testing tools
- Test error scenarios
- Validate response formats
- Monitor performance metrics

## Troubleshooting
Common issues and solutions:
- Connection timeouts: Check network connectivity
- Authentication errors: Verify credentials
- Rate limiting: Implement proper retry logic"""

            # Process content through V2 engine
            process_response = requests.post(
                f"{self.backend_url}/content/process",
                json={"content": test_content},
                timeout=60
            )
            
            assert process_response.status_code == 200, f"Processing failed: {process_response.status_code}"
            process_data = process_response.json()
            
            # Verify V2 processing
            assert process_data.get('engine') == 'v2', "Should use V2 engine"
            assert process_data.get('status') == 'completed', "Processing should complete successfully"
            
            # Check if per-article outlines were created (this would be in the processing logs)
            job_id = process_data.get('job_id')
            assert job_id, "Should have job_id for tracking"
            
            # Verify articles were created with V2 metadata
            content_library_response = requests.get(f"{self.backend_url}/content-library", timeout=10)
            assert content_library_response.status_code == 200, "Content Library should be accessible"
            
            library_data = content_library_response.json()
            articles = library_data.get('articles', [])
            
            # Find articles from our test processing
            v2_articles = [article for article in articles if article.get('metadata', {}).get('engine') == 'v2']
            assert len(v2_articles) > 0, "Should have V2 processed articles"
            
            # Check for per-article outline metadata
            articles_with_outlines = [
                article for article in v2_articles 
                if 'per_article_outlines' in article.get('metadata', {})
            ]
            
            self.log_test("Database Integration", True,
                         f"V2 processing successful with {len(v2_articles)} V2 articles, {len(articles_with_outlines)} with outline metadata")
            return True
            
        except Exception as e:
            self.log_test("Database Integration", False, f"Error: {e}")
            return False
    
    async def test_processing_pipeline_integration(self):
        """Test process_text_content_v2() includes per-article outline creation"""
        try:
            # Test comprehensive content processing
            comprehensive_content = """# Complete Web Development Guide

## Frontend Development
Frontend development involves creating user interfaces and user experiences.

### HTML Fundamentals
HTML provides the structure for web pages:
```html
<!DOCTYPE html>
<html>
<head>
    <title>My Page</title>
</head>
<body>
    <h1>Welcome</h1>
</body>
</html>
```

### CSS Styling
CSS controls the presentation and layout:
```css
body {
    font-family: Arial, sans-serif;
    margin: 0;
    padding: 20px;
}
```

### JavaScript Interactivity
JavaScript adds dynamic behavior:
```javascript
document.addEventListener('DOMContentLoaded', function() {
    console.log('Page loaded');
});
```

## Backend Development
Backend development handles server-side logic and data management.

### Server Setup
Setting up a basic server:
```javascript
const express = require('express');
const app = express();
app.listen(3000, () => console.log('Server running'));
```

### Database Integration
Connecting to databases:
```javascript
const mongoose = require('mongoose');
mongoose.connect('mongodb://localhost:27017/myapp');
```

## Deployment Strategies
Various deployment options are available:
- Cloud platforms (AWS, Azure, GCP)
- Container orchestration (Docker, Kubernetes)
- Static site hosting (Netlify, Vercel)

## Performance Optimization
Key optimization techniques:
1. Code splitting and lazy loading
2. Image optimization and compression
3. Caching strategies
4. Database query optimization

## Security Best Practices
Essential security measures:
- Input validation and sanitization
- Authentication and authorization
- HTTPS encryption
- Regular security audits"""

            # Process through V2 engine
            process_response = requests.post(
                f"{self.backend_url}/content/process",
                json={"content": comprehensive_content},
                timeout=120  # Longer timeout for comprehensive content
            )
            
            assert process_response.status_code == 200, f"Processing failed: {process_response.status_code}"
            process_data = process_response.json()
            
            # Verify V2 processing with enhanced analysis
            assert process_data.get('engine') == 'v2', "Should use V2 engine"
            assert process_data.get('status') == 'completed', "Processing should complete"
            
            # Check for enhanced analysis fields
            enhanced_analysis = process_data.get('enhanced_analysis', {})
            assert isinstance(enhanced_analysis, dict), "Should have enhanced analysis"
            
            # Verify per-article outlines are included in enhanced analysis
            per_article_outlines = enhanced_analysis.get('per_article_outlines', [])
            assert isinstance(per_article_outlines, list), "per_article_outlines should be a list"
            
            # Verify processing includes multi-dimensional analysis
            assert 'content_type' in enhanced_analysis, "Should have content type analysis"
            assert 'audience' in enhanced_analysis, "Should have audience analysis"
            
            self.log_test("Processing Pipeline Integration", True,
                         f"V2 processing pipeline includes per-article outlines ({len(per_article_outlines)} outlines) and enhanced analysis")
            return True
            
        except Exception as e:
            self.log_test("Processing Pipeline Integration", False, f"Error: {e}")
            return False
    
    async def test_file_upload_processing(self):
        """Test file upload processing includes per-article outlining"""
        try:
            # Create a test file with comprehensive content
            test_file_content = """API Integration Best Practices

Introduction
This document provides comprehensive guidelines for API integration best practices.

Authentication and Security
Proper authentication is essential for secure API integration.

API Key Management
- Store API keys securely
- Rotate keys regularly
- Use environment variables
- Never commit keys to version control

OAuth 2.0 Implementation
OAuth 2.0 provides secure authorization:
1. Register your application
2. Obtain client credentials
3. Implement authorization flow
4. Handle token refresh

Error Handling Strategies
Robust error handling improves user experience:
- Implement retry logic with exponential backoff
- Log errors for debugging
- Provide meaningful error messages
- Handle rate limiting gracefully

Rate Limiting and Throttling
Respect API rate limits:
- Monitor usage patterns
- Implement client-side throttling
- Cache responses when appropriate
- Use batch operations when available

Testing and Monitoring
Comprehensive testing ensures reliability:
- Unit tests for individual functions
- Integration tests for workflows
- Load testing for performance
- Monitoring for production issues

Documentation and Maintenance
Keep documentation current:
- Document all endpoints and parameters
- Provide code examples
- Update documentation with changes
- Maintain version compatibility"""

            # Create temporary file
            import tempfile
            with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as temp_file:
                temp_file.write(test_file_content)
                temp_file_path = temp_file.name
            
            try:
                # Upload file for processing
                with open(temp_file_path, 'rb') as file:
                    files = {'file': ('api_guide.txt', file, 'text/plain')}
                    upload_response = requests.post(
                        f"{self.backend_url}/content/upload",
                        files=files,
                        timeout=120
                    )
                
                assert upload_response.status_code == 200, f"File upload failed: {upload_response.status_code}"
                upload_data = upload_response.json()
                
                # Verify V2 processing
                assert upload_data.get('engine') == 'v2', "File upload should use V2 engine"
                assert upload_data.get('status') == 'completed', "File processing should complete"
                
                # Check for enhanced analysis
                enhanced_analysis = upload_data.get('enhanced_analysis', {})
                assert isinstance(enhanced_analysis, dict), "Should have enhanced analysis"
                
                # Verify per-article outlines in file processing
                per_article_outlines = enhanced_analysis.get('per_article_outlines', [])
                assert isinstance(per_article_outlines, list), "Should have per-article outlines from file processing"
                
                # Verify articles were created
                articles_generated = upload_data.get('articles_generated', 0)
                assert articles_generated > 0, "Should generate articles from file"
                
                self.log_test("File Upload Processing", True,
                             f"File upload processing includes per-article outlines ({len(per_article_outlines)} outlines) and generated {articles_generated} articles")
                return True
                
            finally:
                # Clean up temporary file
                import os
                os.unlink(temp_file_path)
                
        except Exception as e:
            self.log_test("File Upload Processing", False, f"Error: {e}")
            return False
    
    async def run_all_tests(self):
        """Run all V2 Engine Step 6 tests"""
        print("🚀 V2 ENGINE STEP 6 PER-ARTICLE OUTLINE TESTING STARTED")
        print("=" * 80)
        
        # Test sequence
        tests = [
            self.test_v2_per_article_outline_planner_instantiation,
            self.test_create_per_article_outlines_function,
            self.test_create_detailed_article_outline,
            self.test_create_blocks_for_article_preview,
            self.test_block_allocation_verification,
            self.test_section_structure_creation,
            self.test_enhanced_content_features,
            self.test_database_integration,
            self.test_processing_pipeline_integration,
            self.test_file_upload_processing
        ]
        
        passed = 0
        total = len(tests)
        
        for test in tests:
            try:
                result = await test()
                if result:
                    passed += 1
            except Exception as e:
                print(f"❌ Test {test.__name__} failed with exception: {e}")
        
        print("=" * 80)
        print(f"🎯 V2 ENGINE STEP 6 TESTING COMPLETE: {passed}/{total} tests passed ({(passed/total)*100:.1f}%)")
        
        if passed == total:
            print("🎉 ALL TESTS PASSED - V2 Engine Step 6 Per-Article Outline implementation is FULLY OPERATIONAL")
        else:
            print(f"⚠️ {total - passed} tests failed - Review implementation")
        
        return passed, total

async def main():
    """Main test execution"""
    tester = V2Step6PerArticleOutlineTest()
    passed, total = await tester.run_all_tests()
    
    # Return appropriate exit code
    return 0 if passed == total else 1

if __name__ == "__main__":
    import sys
    exit_code = asyncio.run(main())
    sys.exit(exit_code)