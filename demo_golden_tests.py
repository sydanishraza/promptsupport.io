#!/usr/bin/env python3
"""
KE-PR10: Golden Tests Framework Demo
Demonstrates the golden test framework functionality
"""

import asyncio
import json
import pathlib
import sys
import os

# Add paths for imports
sys.path.insert(0, '/app')
sys.path.insert(0, '/app/backend')

async def demo_golden_framework():
    """Demonstrate the golden test framework"""
    
    print("🧪 KE-PR10: Golden Tests Framework Demo")
    print("=" * 60)
    
    try:
        # Import framework components
        from tests.conftest import (
            normalize_html, 
            compare_json, 
            save_golden_baseline
        )
        
        print("✅ Framework imports successful")
        
        # Demo 1: HTML Normalization
        print("\n📋 Demo 1: HTML Normalization")
        normalize_fn = normalize_html()
        
        test_html = '''
        <div id="uuid-12345-abcdef" class="test">
            <p>Created at: 2024-01-15T10:30:00Z</p>
            <span>Run ID: abc-def-123-456</span>
            <meta name="timestamp" content="2024-01-15T10:30:00.123Z">
        </div>
        '''
        
        normalized = normalize_fn(test_html)
        print(f"Original: {test_html.strip()}")
        print(f"Normalized: {normalized}")
        
        # Demo 2: JSON Comparison with Tolerance
        print("\n📊 Demo 2: JSON Comparison with Tolerance")
        compare_fn = compare_json()
        
        expected_qa = {
            "coverage_percent": 87.5,
            "total_issues": 2,
            "metrics": {"processing_time": 1250.3}
        }
        
        actual_qa = {
            "coverage_percent": 87.2,  # Slightly lower
            "total_issues": 2,
            "metrics": {"processing_time": 1251.1}  # Slightly higher
        }
        
        comparison = compare_fn(expected_qa, actual_qa, tolerance=0.5)
        print(f"Expected: {expected_qa}")
        print(f"Actual: {actual_qa}")
        print(f"Match: {comparison['match']}")
        if not comparison['match']:
            print(f"Differences: {comparison['differences']}")
        
        # Demo 3: Mock Pipeline Results
        print("\n🔧 Demo 3: Mock Pipeline Results")
        
        input_file = pathlib.Path('/app/tests/golden/input/sample3.md')
        if input_file.exists():
            
            # Simulate pipeline processing
            mock_result = {
                "qa": {
                    "coverage_percent": 87.5,
                    "total_issues": 2,
                    "critical_issues": 0,
                    "processing_timestamp": "2024-01-15T10:30:00Z"
                },
                "anchors": [
                    {
                        "level": 1,
                        "text": "MongoDB Repository Pattern Integration Guide",
                        "anchor": "mongodb-repository-pattern-integration-guide",
                        "id": "mongodb-repository-pattern-integration-guide"
                    },
                    {
                        "level": 2, 
                        "text": "Overview",
                        "anchor": "overview",
                        "id": "overview"
                    }
                ],
                "toc": [
                    {
                        "title": "MongoDB Repository Pattern Integration Guide",
                        "anchor": "#mongodb-repository-pattern-integration-guide",
                        "level": 1
                    },
                    {
                        "title": "Overview", 
                        "anchor": "#overview",
                        "level": 2
                    }
                ],
                "html": "<h1 id='mongodb-repository-pattern-integration-guide'>MongoDB Repository Pattern Integration Guide</h1><h2 id='overview'>Overview</h2><p>Mock processed content...</p>"
            }
            
            print(f"✅ Mock pipeline result generated for {input_file.name}")
            print(f"  - Coverage: {mock_result['qa']['coverage_percent']}%")
            print(f"  - Anchors: {len(mock_result['anchors'])} headings")
            print(f"  - TOC: {len(mock_result['toc'])} entries")
            print(f"  - HTML: {len(mock_result['html'])} characters")
            
        else:
            print(f"❌ Input file not found: {input_file}")
        
        # Demo 4: Framework Validation
        print("\n✅ Demo 4: Framework Validation")
        
        # Check if baselines exist
        expected_dir = pathlib.Path('/app/tests/golden/expected')
        baseline_files = list(expected_dir.glob('sample3.*'))
        
        if baseline_files:
            print(f"✅ Found {len(baseline_files)} baseline files:")
            for file in sorted(baseline_files):
                print(f"  - {file.name} ({file.stat().st_size} bytes)")
        else:
            print("⚠️ No baseline files found - run with --update-golden to create them")
        
        # Demo 5: Coverage Calculation
        print("\n📈 Demo 5: Coverage Calculation")
        
        # Simulate coverage calculation
        total_content_elements = 100
        processed_elements = 87.5
        coverage_percent = (processed_elements / total_content_elements) * 100
        
        print(f"Content elements: {total_content_elements}")
        print(f"Processed elements: {processed_elements}")
        print(f"Coverage: {coverage_percent:.1f}%")
        
        # Check threshold
        threshold = 80.0
        tolerance = 0.5
        
        if coverage_percent >= (threshold - tolerance):
            print(f"✅ Coverage {coverage_percent:.1f}% meets threshold {threshold}% (tolerance: ±{tolerance}%)")
        else:
            print(f"❌ Coverage {coverage_percent:.1f}% below threshold {threshold}% (tolerance: ±{tolerance}%)")
        
        print("\n🎉 Golden Tests Framework Demo Complete!")
        print("Framework is ready for comprehensive regression testing.")
        
        return True
        
    except Exception as e:
        print(f"❌ Demo failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Run the demo"""
    print("Starting KE-PR10 Golden Tests Framework Demo...")
    
    success = asyncio.run(demo_golden_framework())
    
    if success:
        print("\n✅ Demo completed successfully!")
        print("\nNext steps:")
        print("1. Run: pytest tests/golden/test_pipeline.py --update-golden")
        print("2. Run: pytest tests/golden/test_pipeline.py -v")
        print("3. Check: tests/golden/README.md for full documentation")
    else:
        print("\n❌ Demo failed - check error messages above")
        sys.exit(1)

if __name__ == "__main__":
    main()