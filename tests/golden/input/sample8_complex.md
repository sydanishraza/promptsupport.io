# KE-PR10: Golden Tests & Non-Regression Suite - Complex Document

## Executive Summary

This complex document tests the complete V2 engine processing pipeline with multiple content types, embedded media, code samples, tables, lists, cross-references, and advanced formatting to ensure comprehensive golden test coverage.

### Key Testing Areas

- **Multi-level headings** with complex hierarchy
- **Code blocks** in multiple languages
- **Tables** with various formatting
- **Lists** (ordered, unordered, nested)
- **Cross-references** and internal links
- **Media references** and placeholders
- **Special formatting** and edge cases

## Table of Contents

1. [Introduction](#introduction)
2. [Technical Implementation](#technical-implementation)  
3. [Code Examples](#code-examples)
4. [Data Structures](#data-structures)
5. [API Reference](#api-reference)
6. [Testing Scenarios](#testing-scenarios)
7. [Performance Benchmarks](#performance-benchmarks)
8. [Troubleshooting Guide](#troubleshooting-guide)
9. [Conclusion](#conclusion)

---

## Introduction

The PromptSupport V2 engine processes diverse content types through a sophisticated pipeline that maintains **TICKET-3 compliance** while ensuring **high-quality output** with **comprehensive metadata preservation**.

### Processing Pipeline Stages

The V2 engine implements the following processing stages:

1. **Content Analysis** - Extract structure and metadata
2. **Normalization** - Convert to canonical format  
3. **Enhancement** - Add cross-references and links
4. **Validation** - Quality assurance checks
5. **Publishing** - Final output generation

> **Note**: Each stage includes comprehensive error handling and fallback mechanisms to ensure **87.5% success rate** or higher.

### Golden Test Coverage

This document validates:

- ✅ **Heading extraction** and anchor generation
- ✅ **TOC generation** with proper linking
- ✅ **QA metrics** calculation and reporting  
- ✅ **Cross-reference** preservation and validation
- ✅ **Code block** processing and syntax highlighting
- ✅ **Table** structure preservation
- ✅ **List** formatting (ordered, unordered, nested)
- ✅ **Media** reference handling

## Technical Implementation

### Repository Pattern Integration

The KE-PR9 repository pattern provides centralized data access:

```python
from app.engine.stores.mongo import RepositoryFactory

# Get repository instances
content_repo = RepositoryFactory.get_content_library()
qa_repo = RepositoryFactory.get_qa_results()

# Insert article with TICKET-3 fields
article = {
    "title": "Sample Article",
    "content": processed_content,
    "doc_uid": generate_doc_uid(),
    "doc_slug": generate_doc_slug(title),
    "headings": extract_headings(content),
    "xrefs": extract_cross_references(content)
}

article_id = await content_repo.insert_article(article)
```

### Error Handling Strategy

```javascript
// JavaScript error handling example
async function processContent(content) {
    try {
        const result = await pipeline.run(content);
        
        if (result.qa_report.coverage_percent < 80) {
            throw new Error(`Low coverage: ${result.qa_report.coverage_percent}%`);
        }
        
        return result;
        
    } catch (error) {
        console.error('Processing failed:', error.message);
        
        // Fallback processing
        return await fallbackProcessor.run(content);
    }
}
```

### Configuration Management

```yaml
# YAML configuration example
pipeline:
  v2_engine:
    enabled: true
    features:
      - repository_pattern
      - ticket3_support
      - woolf_style_processing
      - structural_linting
    
    thresholds:
      coverage_minimum: 80.0
      processing_timeout: 300
      max_file_size: 10485760  # 10MB
      
    repository:
      connection_timeout: 30
      fallback_enabled: true
      error_retry_count: 3
```

## Code Examples

### Shell Script Processing

```bash
#!/bin/bash

# Golden test execution script
GOLDEN_DIR="/app/tests/golden"
RESULTS_DIR="${GOLDEN_DIR}/results"

echo "🧪 Running KE-PR10 Golden Tests"

# Create results directory
mkdir -p "${RESULTS_DIR}"

# Run pytest with coverage
pytest "${GOLDEN_DIR}/test_pipeline.py" \
    --cov=app \
    --cov-report=html:"${RESULTS_DIR}/coverage" \
    --junitxml="${RESULTS_DIR}/junit.xml" \
    -v

# Check exit code
if [ $? -eq 0 ]; then
    echo "✅ All golden tests passed"
else
    echo "❌ Golden tests failed - check artifacts"
    exit 1
fi
```

### SQL Query Examples

```sql
-- Database query for QA metrics
SELECT 
    run_id,
    AVG(coverage_percent) as avg_coverage,
    COUNT(*) as total_articles,
    SUM(CASE WHEN critical_issues = 0 THEN 1 ELSE 0 END) as clean_articles
FROM v2_validation_results 
WHERE timestamp >= NOW() - INTERVAL '24 hours'
GROUP BY run_id
ORDER BY avg_coverage DESC;

-- Performance monitoring query
SELECT 
    DATE(processing_timestamp) as date,
    AVG(processing_time_ms) as avg_time,
    MAX(processing_time_ms) as max_time,
    COUNT(*) as processed_count
FROM processing_metrics 
WHERE engine = 'v2'
GROUP BY DATE(processing_timestamp)
ORDER BY date DESC;
```

### CSS Styling Examples

```css
/* Golden test report styling */
.golden-test-results {
    font-family: 'Inter', sans-serif;
    max-width: 1200px;
    margin: 0 auto;
    padding: 2rem;
}

.test-status {
    display: inline-block;
    padding: 0.25rem 0.75rem;
    border-radius: 12px;
    font-weight: 600;
    font-size: 0.875rem;
}

.test-status.passed {
    background-color: #d4edda;
    color: #155724;
    border: 1px solid #c3e6cb;
}

.test-status.failed {
    background-color: #f8d7da;
    color: #721c24;
    border: 1px solid #f5c6cb;
}

.coverage-meter {
    width: 100%;
    height: 20px;
    background-color: #e9ecef;
    border-radius: 10px;
    overflow: hidden;
}

.coverage-fill {
    height: 100%;
    background: linear-gradient(90deg, #28a745 0%, #20c997 100%);
    transition: width 0.3s ease;
}
```

## Data Structures

### Article Metadata Schema

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `id` | String | Yes | Unique article identifier |
| `doc_uid` | String | Yes | TICKET-3 universal document ID |
| `doc_slug` | String | Yes | URL-friendly document slug |
| `title` | String | Yes | Article title |
| `content` | String | Yes | Processed article content |
| `html` | String | Yes | Final HTML output |
| `headings` | Array | Yes | Extracted heading structure |
| `xrefs` | Array | Yes | Cross-reference registry |
| `created_at` | DateTime | Yes | Creation timestamp |
| `updated_at` | DateTime | Yes | Last update timestamp |
| `engine` | String | Yes | Processing engine version |
| `metadata` | Object | No | Additional processing metadata |

### QA Report Structure

```json
{
  "validation_id": "val_abc123",
  "run_id": "run_def456",
  "coverage_percent": 87.5,
  "total_issues": 3,
  "critical_issues": 0,
  "issues": [
    {
      "type": "formatting",
      "severity": "minor",
      "message": "Inconsistent heading spacing",
      "location": "section-2"
    }
  ],
  "metrics": {
    "processing_time_ms": 1250,
    "content_length": 15420,
    "headings_count": 12,
    "links_count": 8,
    "code_blocks": 4
  },
  "timestamp": "2024-01-15T10:30:00Z"
}
```

### Benchmark Results Matrix

| Content Type | Size (KB) | Processing Time (ms) | Coverage (%) | Memory (MB) |
|--------------|-----------|----------------------|--------------|-------------|
| **Markdown** | 5.2 | 245 | 92.1 | 12.3 |
| **HTML** | 8.7 | 378 | 89.4 | 18.7 |
| **DOCX** | 15.3 | 892 | 86.2 | 34.5 |
| **PDF** | 23.1 | 1456 | 83.7 | 52.1 |
| **Text** | 3.8 | 156 | 95.3 | 8.9 |
| **Complex** | 45.2 | 2341 | 88.8 | 78.4 |

## API Reference

### Content Processing Endpoints

#### POST /api/content/process

Process content through V2 pipeline with comprehensive options.

**Request Parameters:**

- `content` (string, required): Raw content to process
- `content_type` (enum): One of `markdown`, `html`, `text`, `docx`, `pdf`
- `processing_mode` (enum): `v2_only`, `hybrid`, `v1_fallback`
- `options` (object): Processing configuration

**Response Format:**

```json
{
  "status": "success|error",
  "articles": [...],
  "processing_time": 1.25,
  "qa_report": {...},
  "metadata": {...}
}
```

#### GET /api/content/library

Retrieve content library with filtering and pagination.

**Query Parameters:**

- `limit` (integer): Maximum number of results (default: 100)
- `offset` (integer): Pagination offset (default: 0)
- `engine` (string): Filter by engine version
- `search` (string): Full-text search query
- `sort` (string): Sort field (`created_at`, `title`, `coverage`)
- `order` (string): Sort order (`asc`, `desc`)

### TICKET-3 Operations

#### POST /api/ticket3/backfill-bookmarks

Backfill TICKET-3 fields for existing articles.

**Features:**
- ✅ Batch processing with configurable limits
- ✅ Progress tracking and error reporting
- ✅ Selective field updates (doc_uid, doc_slug, headings, xrefs)
- ✅ Validation and integrity checks

#### GET /api/ticket3/document-registry/{doc_uid}

Retrieve document registry information for cross-reference resolution.

## Testing Scenarios

### Scenario 1: Basic Markdown Processing

**Input:**
```markdown
# Sample Document
## Section 1
Content here...
### Subsection 1.1
More content...
```

**Expected Outputs:**
- `sample.anchors.json`: Heading anchors and IDs
- `sample.toc.json`: Table of contents hierarchy  
- `sample.qa.json`: Quality metrics (coverage >= 85%)
- `sample.html`: Processed HTML output

### Scenario 2: Complex Document with Media

**Input:** Multi-format document with:
- Nested headings (6 levels deep)
- Code blocks in 5+ languages
- Tables with 10+ columns
- Lists with 3+ nesting levels
- 20+ cross-references
- Media placeholders

**Validation Criteria:**
- Coverage >= 80% (tolerance: 0.5%)
- All headings have stable anchor IDs
- TOC links resolve correctly
- Code blocks preserve syntax
- Tables maintain structure
- Cross-references validate

### Scenario 3: Edge Cases and Error Handling

**Test Cases:**
1. **Empty content**: Should generate minimal valid output
2. **Malformed HTML**: Should clean and process successfully
3. **Extremely long content**: Should process within timeout limits
4. **Unicode characters**: Should preserve encoding correctly
5. **Binary content**: Should handle gracefully with error messages

### Scenario 4: Performance and Scalability

**Benchmarks:**
- Process 100 documents in < 60 seconds
- Memory usage < 200MB for batch processing
- Coverage consistency within 1% across runs
- Zero data corruption in concurrent processing

## Performance Benchmarks

### Processing Time Analysis

```python
# Performance measurement example
import time
from app.engine.v2.pipeline import Pipeline

def benchmark_processing():
    """Benchmark V2 pipeline performance"""
    test_sizes = [1, 5, 10, 25, 50, 100]  # KB
    results = []
    
    for size in test_sizes:
        content = generate_test_content(size * 1024)
        
        start_time = time.time()
        result = pipeline.run(content)
        end_time = time.time()
        
        processing_time = (end_time - start_time) * 1000  # ms
        
        results.append({
            'size_kb': size,
            'processing_time_ms': processing_time,
            'coverage_percent': result.qa_report.coverage_percent,
            'throughput_kb_per_sec': size / (processing_time / 1000)
        })
    
    return results
```

### Memory Usage Profiling

```bash
# Memory profiling with valgrind
valgrind --tool=massif --massif-out-file=golden-test.massif \
    python -m pytest tests/golden/test_pipeline.py::test_golden_complex_document_pipeline

# Analyze results
ms_print golden-test.massif > memory-profile.txt

# Extract peak usage
grep "peak" memory-profile.txt
```

### Coverage Trending

| Date | Coverage (%) | Δ from Baseline | Status |
|------|--------------|-----------------|--------|
| 2024-01-10 | 85.2 | +0.2% | ✅ Pass |
| 2024-01-11 | 86.1 | +1.1% | ✅ Pass |
| 2024-01-12 | 87.5 | +2.5% | ✅ Pass |
| 2024-01-13 | 87.3 | +2.3% | ✅ Pass |
| 2024-01-14 | 88.1 | +3.1% | ✅ Pass |
| 2024-01-15 | 87.8 | +2.8% | ✅ Pass |

## Troubleshooting Guide

### Common Test Failures

#### 1. Coverage Regression

**Symptoms:**
- Coverage drops below baseline - 0.5%
- QA reports show increased critical issues
- Processing time increases significantly

**Resolution:**
1. Check recent code changes in analyzer/generator stages
2. Verify LLM integration is functioning correctly
3. Review timeout configurations
4. Run individual pipeline stages for isolation

#### 2. Anchor Drift Detection

**Symptoms:**
- Heading IDs change between runs
- Cross-references become broken
- TOC links point to incorrect targets

**Resolution:**
1. Ensure heading text normalization is deterministic
2. Check slug generation algorithm for randomness
3. Verify text processing order consistency
4. Review anchor ID generation logic

#### 3. HTML Output Changes

**Symptoms:**
- Normalized HTML differs from baseline
- Template modifications affect output
- Styling or structure changes detected

**Resolution:**
1. Update HTML normalization rules if needed
2. Review template changes for intentional modifications
3. Check CSS/JavaScript injection points
4. Verify metadata field updates don't affect structure

#### 4. Performance Degradation

**Symptoms:**
- Processing times exceed baseline + 20%
- Memory usage grows beyond limits
- Timeout errors in complex documents

**Resolution:**
1. Profile code for performance hotspots
2. Check database query optimization
3. Review memory allocation patterns
4. Optimize LLM API calls and caching

### Debug Commands

```bash
# Run specific golden test with verbose output
pytest tests/golden/test_pipeline.py::test_golden_markdown_pipeline -v -s

# Update specific baseline
pytest tests/golden/test_pipeline.py::test_golden_markdown_pipeline --update-golden

# Run with coverage reporting
pytest tests/golden/ --cov=app --cov-report=html

# Run performance benchmarks
pytest tests/golden/test_pipeline.py::TestGoldenPerformance -v

# Generate diff artifacts
pytest tests/golden/ --tb=short --diff-artifacts=/tmp/golden-diffs
```

### Log Analysis

```python
# Extract processing metrics from logs
import re
from datetime import datetime

def analyze_processing_logs(log_file):
    """Analyze V2 processing logs for performance metrics"""
    
    patterns = {
        'processing_time': r'Processing completed in (\d+\.?\d*)ms',
        'coverage': r'Coverage: (\d+\.?\d*)%',
        'articles_generated': r'Generated (\d+) articles',
        'errors': r'ERROR.*V2 pipeline'
    }
    
    metrics = []
    
    with open(log_file, 'r') as f:
        for line in f:
            timestamp = extract_timestamp(line)
            
            for metric, pattern in patterns.items():
                match = re.search(pattern, line)
                if match:
                    metrics.append({
                        'timestamp': timestamp,
                        'metric': metric,
                        'value': match.group(1)
                    })
    
    return metrics
```

## Conclusion

The KE-PR10 Golden Tests & Non-Regression Suite provides comprehensive protection against regressions in the V2 engine processing pipeline. This complex document validates all major processing capabilities including:

### ✅ Validated Features

1. **Multi-level heading processing** with stable anchor generation
2. **Code block preservation** across multiple programming languages  
3. **Table structure maintenance** with complex formatting
4. **List processing** (ordered, unordered, nested hierarchies)
5. **Cross-reference tracking** and validation
6. **Media reference handling** with placeholder generation
7. **Performance benchmarking** with automated threshold enforcement
8. **Error handling** and graceful degradation testing

### 📊 Success Metrics

- **Coverage Target**: >= 80% (current: 87.8%)
- **Processing Performance**: < 50ms per KB content
- **Memory Efficiency**: < 10MB growth per document
- **Anchor Stability**: 100% deterministic generation
- **Test Coverage**: 95% of pipeline functionality validated

### 🔄 Continuous Integration

The golden test framework integrates with CI/CD pipelines to:

- **Prevent regression deployment** through automated quality gates
- **Generate diff artifacts** for easy failure analysis  
- **Track coverage trends** over time with alerting
- **Validate performance** against established benchmarks
- **Ensure deterministic behavior** across environments

### 🚀 Future Enhancements

Planned improvements to the golden test framework:

1. **Extended fixture library** with domain-specific content
2. **Visual regression testing** for HTML output rendering
3. **Performance profiling** integration with CI metrics
4. **Automated baseline updates** for approved changes
5. **Cross-environment validation** (dev, staging, production)

The golden test suite ensures the V2 engine maintains **high quality**, **performance**, and **reliability** while enabling **confident development** and **safe deployment** of improvements.

---

**Document Metadata:**
- **Processing Engine**: V2 Pipeline with Repository Pattern
- **Golden Test Coverage**: 100% (all major features validated)
- **Performance Target**: Met (< 50ms/KB processing time)
- **Quality Gate Status**: ✅ PASSED
- **Generated**: 2024-01-15T10:30:00Z
- **Test Framework**: KE-PR10 Golden Tests & Non-Regression Suite