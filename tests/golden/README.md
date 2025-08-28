# KE-PR10: Golden Tests & Non-Regression Suite

## Overview

The Golden Tests framework provides comprehensive regression protection for the PromptSupport V2 engine processing pipeline. It validates pipeline behavior against known baseline outputs to ensure consistent, high-quality processing across code changes.

## Directory Structure

```
tests/golden/
├── input/                    # Golden test fixtures
│   ├── sample1.docx         # Microsoft Word document
│   ├── sample2.pdf          # PDF document  
│   ├── sample3.md           # Markdown content
│   ├── sample4.html         # HTML with CSS/JS
│   ├── sample5.txt          # Plain text content
│   ├── sample6_url.html     # URL-sourced HTML
│   ├── sample7.mp4          # Media file placeholder
│   └── sample8_complex.md   # Complex multi-element document
├── expected/                # Baseline outputs (generated)
│   ├── sample1.anchors.json # Heading anchor structure
│   ├── sample1.toc.json     # Table of contents
│   ├── sample1.qa.json      # Quality assurance metrics
│   ├── sample1.html         # Final HTML output
│   └── [additional baselines...]
├── test_pipeline.py         # Main golden test suite
└── README.md               # This documentation
```

## Running Golden Tests

### Basic Test Execution

```bash
# Run all golden tests
pytest tests/golden/test_pipeline.py -v

# Run specific test
pytest tests/golden/test_pipeline.py::TestGoldenPipeline::test_golden_markdown_pipeline -v

# Run with coverage reporting
pytest tests/golden/ --cov=app --cov-report=html
```

### Baseline Management

```bash
# Update all baselines (after intentional changes)
pytest tests/golden/test_pipeline.py --update-golden

# Update specific baseline
pytest tests/golden/test_pipeline.py::test_golden_markdown_pipeline --update-golden

# Dry run - see what would be updated
pytest tests/golden/test_pipeline.py --update-golden --collect-only
```

## Test Coverage Areas

### 1. Content Processing Types
- **DOCX**: Microsoft Word document processing
- **PDF**: PDF extraction and conversion
- **Markdown**: Structured markdown with headings, code, tables
- **HTML**: Web content with CSS, JavaScript, complex formatting
- **Text**: Plain text processing with structure detection
- **URL HTML**: Web-scraped content processing
- **Media**: Video/audio file handling (placeholder-based)
- **Complex**: Multi-element documents with all content types

### 2. Pipeline Validation Points
- **QA Reports**: Coverage percentages, issue counts, metrics
- **Anchor Generation**: Heading IDs, bookmark registry, stability
- **TOC Structure**: Table of contents hierarchy and linking
- **HTML Output**: Final processed content with normalization

### 3. Regression Protection
- **Coverage Thresholds**: Minimum 80% coverage with 0.5% tolerance
- **Anchor Stability**: Deterministic heading ID generation
- **Performance Limits**: Processing time and memory usage bounds
- **Quality Gates**: Critical issue counts and validation passes

## Baseline Refresh Workflow

### When to Update Baselines

Update golden baselines when making **intentional, approved** changes to:
- V2 processing pipeline behavior
- Output formatting or structure
- QA calculation methods  
- Anchor generation algorithms

### Safe Update Process

1. **Review Changes**: Ensure updates are intentional and approved
   ```bash
   # Check current test failures to understand changes
   pytest tests/golden/ -v
   ```

2. **Update Baselines**: Use the update flag carefully
   ```bash
   # Update all baselines
   pytest tests/golden/test_pipeline.py --update-golden
   ```

3. **Validate Updates**: Review generated baseline files
   ```bash
   # Check generated files look correct
   ls -la tests/golden/expected/
   
   # Review specific baseline content
   cat tests/golden/expected/sample3.qa.json
   ```

4. **Commit Changes**: Include clear description of what changed
   ```bash
   git add tests/golden/expected/
   git commit -m "Update golden baselines for [specific change description]"
   ```

### ⚠️ Important Warnings

- **Never update baselines automatically** in CI/CD pipelines
- **Always review** baseline changes before committing
- **Document rationale** for baseline updates in commit messages
- **Test thoroughly** after baseline updates to ensure correctness

## Test Framework Features

### Coverage Enforcement
Tests enforce minimum coverage thresholds with float tolerance:

```python
# Coverage comparison with tolerance
expected_coverage = 85.0
actual_coverage = 84.7
tolerance = 0.5

# This passes: 84.7 >= (85.0 - 0.5)
assert actual_coverage >= expected_coverage - tolerance
```

### HTML Normalization
HTML content is normalized for stable comparisons:

- **Timestamps** → `TIMESTAMP` placeholder
- **UUIDs/Random IDs** → `UUID` or `NORMALIZED_ID` placeholders  
- **Whitespace** → Standardized spacing
- **Metadata** → Processing-specific fields normalized

### JSON Comparison
Structured comparison with tolerance for floating-point values:

```python
# Tolerant comparison for QA metrics
expected = {"coverage_percent": 85.0, "issues": 5}
actual = {"coverage_percent": 84.7, "issues": 5}

# Passes with default 0.5% tolerance
result = compare_json(expected, actual, tolerance=0.5)
assert result["match"] is True
```

### Error Handling
Robust error handling with fallback processing:

- Repository operation failures fall back to direct database access
- Processing timeouts return minimal valid results
- Invalid content generates error reports with metadata
- All failures are logged with detailed context

## CI Integration

### Automated Testing
The CI pipeline runs golden tests automatically:

```yaml
# Example CI configuration
golden_tests:
  runs-on: ubuntu-latest
  steps:
    - uses: actions/checkout@v3
    - name: Run Golden Tests
      run: |
        pytest tests/golden/test_pipeline.py -v \
          --cov=app \
          --cov-report=xml \
          --junitxml=golden-results.xml
    
    - name: Upload Coverage
      uses: codecov/codecov-action@v3
      
    - name: Upload Diff Artifacts
      if: failure()
      uses: actions/upload-artifact@v3
      with:
        name: golden-test-diffs
        path: tests/golden/expected/*_diff.*
```

### Failure Artifacts
When tests fail, CI generates diff artifacts:

- `sample_name_qa_diff.json`: QA metric differences
- `sample_name_anchors_diff.json`: Anchor structure changes
- `sample_name_toc_diff.json`: TOC hierarchy modifications  
- `sample_name_html_diff.txt`: HTML output differences

### Coverage Reporting
Coverage metrics are tracked and reported:

- **Test Coverage**: Percentage of code exercised by tests
- **Pipeline Coverage**: Percentage of V2 processing stages validated
- **Content Coverage**: Percentage of input content successfully processed
- **Regression Detection**: Alerts on coverage drops > 0.5%

## Performance Monitoring

### Benchmarks
Golden tests include performance validation:

```python
# Performance benchmarks per content type
PERFORMANCE_TARGETS = {
    "markdown": {"max_time_ms": 500, "max_memory_mb": 20},
    "html": {"max_time_ms": 800, "max_memory_mb": 30},
    "docx": {"max_time_ms": 2000, "max_memory_mb": 50},
    "pdf": {"max_time_ms": 3000, "max_memory_mb": 70},
    "complex": {"max_time_ms": 5000, "max_memory_mb": 100}
}
```

### Monitoring Metrics
- **Processing Time**: Per document and per KB content
- **Memory Usage**: Peak and growth during processing
- **Throughput**: Documents processed per minute
- **Success Rate**: Percentage of successful processing runs

## Troubleshooting

### Common Issues

#### 1. Coverage Regression
```bash
# Symptoms: Coverage drops below threshold
# Resolution: Check analyzer/generator changes
pytest tests/golden/ -v -k "coverage" --tb=short
```

#### 2. Anchor Drift
```bash
# Symptoms: Heading IDs change between runs  
# Resolution: Review slug generation algorithm
pytest tests/golden/ -v -k "anchor" --tb=short
```

#### 3. HTML Output Changes
```bash
# Symptoms: Normalized HTML differs from baseline
# Resolution: Update normalization rules if needed
pytest tests/golden/ -v -k "html" --tb=short
```

#### 4. Test Timeout
```bash
# Symptoms: Tests hang or exceed time limits
# Resolution: Check processing pipeline performance
timeout 300 pytest tests/golden/test_pipeline.py -v
```

### Debug Commands

```bash
# Verbose test output with full tracebacks
pytest tests/golden/ -v -s --tb=long

# Run single test with debugging
pytest tests/golden/test_pipeline.py::test_golden_markdown_pipeline -v -s --pdb

# Check test discovery
pytest tests/golden/ --collect-only

# Run with profiling
pytest tests/golden/ --profile --profile-svg
```

### Log Analysis

Check test logs for processing details:

```bash
# View recent test logs
tail -f /var/log/supervisor/backend.*.log | grep -i "golden\|test"

# Extract performance metrics
grep "Processing completed" /var/log/supervisor/backend.*.log | tail -20

# Check error patterns
grep -i "error\|exception" /var/log/supervisor/backend.*.log | tail -10
```

## Development Guidelines

### Adding New Golden Tests

1. **Create Input Fixture**: Add new file to `tests/golden/input/`
2. **Generate Baseline**: Run with `--update-golden` to create expected outputs
3. **Add Test Method**: Create corresponding test in `test_pipeline.py`
4. **Validate Results**: Ensure baselines are correct and meaningful
5. **Document Changes**: Update this README with new test coverage

### Fixture Guidelines
- **Comprehensive Content**: Include diverse elements (headings, code, tables, lists)
- **Realistic Size**: Representative of actual usage (1-50KB typical)
- **Edge Cases**: Include boundary conditions and error scenarios
- **Metadata Rich**: Ensure content exercises all pipeline stages

### Baseline Quality
- **Accurate Metrics**: QA reports should reflect actual quality
- **Stable Anchors**: Heading IDs must be deterministic
- **Valid HTML**: Output should be well-formed and semantic
- **Complete Coverage**: All content elements should be processed

## Quality Metrics

### Success Criteria
- **Coverage**: >= 80% content processing success rate
- **Stability**: 100% deterministic anchor generation
- **Performance**: Processing time within established limits
- **Reliability**: < 1% test flakiness rate

### Monitoring Dashboard
Track golden test metrics over time:

- **Daily Coverage Trend**: Rolling 7-day average
- **Processing Performance**: Response time percentiles  
- **Test Reliability**: Success rate and flake detection
- **Baseline Drift**: Frequency of baseline updates

---

## Getting Help

- **Documentation Issues**: Update this README
- **Test Failures**: Check troubleshooting section above
- **Performance Issues**: Review benchmark guidelines
- **Framework Issues**: Contact development team

**Last Updated**: 2024-01-15  
**Framework Version**: KE-PR10 v1.0  
**Compatibility**: V2 Engine Pipeline with Repository Pattern