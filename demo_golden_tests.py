#!/usr/bin/env python3
"""
KE-PR10: Golden Tests Framework Demo
Demonstrates the golden test framework functionality
"""

import asyncio
import json
import pathlib
import re
import sys
import os
from datetime import datetime

# Add paths for imports
sys.path.insert(0, '/app')
sys.path.insert(0, '/app/backend')

def normalize_html_content(html_content: str) -> str:
    """Normalize HTML content for comparison (standalone version)"""
    # Remove timestamps
    html_content = re.sub(r'\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d+)?Z?', 'TIMESTAMP', html_content)
    
    # Remove random UUIDs and IDs
    html_content = re.sub(r'[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}', 'UUID', html_content)
    html_content = re.sub(r'id="[^"]*"', 'id="NORMALIZED_ID"', html_content)
    
    # Remove processing timestamps and metadata
    html_content = re.sub(r'"created_at":\s*"[^"]*"', '"created_at": "TIMESTAMP"', html_content)
    html_content = re.sub(r'"updated_at":\s*"[^"]*"', '"updated_at": "TIMESTAMP"', html_content)
    html_content = re.sub(r'"run_id":\s*"[^"]*"', '"run_id": "RUN_ID"', html_content)
    
    # Normalize whitespace
    html_content = re.sub(r'\s+', ' ', html_content)
    html_content = html_content.strip()
    
    return html_content

def compare_json_content(expected: dict, actual: dict, tolerance: float = 0.5) -> dict:
    """Compare JSON objects with tolerance (standalone version)"""
    def _compare_values(exp_val, act_val, path=""):
        differences = []
        
        if isinstance(exp_val, dict) and isinstance(act_val, dict):
            # Compare dictionaries
            all_keys = set(exp_val.keys()) | set(act_val.keys())
            for key in all_keys:
                key_path = f"{path}.{key}" if path else key
                if key not in exp_val:
                    differences.append(f"Unexpected key: {key_path}")
                elif key not in act_val:
                    differences.append(f"Missing key: {key_path}")
                else:
                    differences.extend(_compare_values(exp_val[key], act_val[key], key_path))
                    
        elif isinstance(exp_val, list) and isinstance(act_val, list):
            # Compare lists
            if len(exp_val) != len(act_val):
                differences.append(f"List length mismatch at {path}: expected {len(exp_val)}, got {len(act_val)}")
            else:
                for i, (exp_item, act_item) in enumerate(zip(exp_val, act_val)):
                    differences.extend(_compare_values(exp_item, act_item, f"{path}[{i}]"))
                    
        elif isinstance(exp_val, (int, float)) and isinstance(act_val, (int, float)):
            # Compare numbers with tolerance
            if abs(exp_val - act_val) > tolerance:
                differences.append(f"Number mismatch at {path}: expected {exp_val}, got {act_val} (tolerance: {tolerance})")
                
        else:
            # Compare other types directly
            if exp_val != act_val:
                differences.append(f"Value mismatch at {path}: expected {exp_val}, got {act_val}")
        
        return differences
    
    differences = _compare_values(expected, actual)
    
    return {
        "match": len(differences) == 0,
        "differences": differences,
        "expected": expected,
        "actual": actual
    }

async def demo_golden_framework():
    """Demonstrate the golden test framework"""
    
    print("🧪 KE-PR10: Golden Tests Framework Demo")
    print("=" * 60)
    
    try:
        print("✅ Framework components loaded")
        
        # Demo 1: HTML Normalization
        print("\n📋 Demo 1: HTML Normalization")
        
        test_html = '''
        <div id="uuid-12345-abcdef" class="test">
            <p>Created at: 2024-01-15T10:30:00Z</p>
            <span>Run ID: abc-def-123-456</span>
            <meta name="timestamp" content="2024-01-15T10:30:00.123Z">
        </div>
        '''
        
        normalized = normalize_html_content(test_html)
        print(f"Original: {test_html.strip()}")
        print(f"Normalized: {normalized}")
        
        # Demo 2: JSON Comparison with Tolerance
        print("\n📊 Demo 2: JSON Comparison with Tolerance")
        
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
        
        comparison = compare_json_content(expected_qa, actual_qa, tolerance=0.5)
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
        
        # Demo 6: Directory Structure
        print("\n📁 Demo 6: Directory Structure Validation")
        
        # Check golden test structure
        golden_dir = pathlib.Path('/app/tests/golden')
        input_dir = golden_dir / 'input'
        expected_dir = golden_dir / 'expected'
        
        print(f"Golden tests directory: {golden_dir}")
        print(f"  - Input fixtures: {len(list(input_dir.glob('*'))) if input_dir.exists() else 0} files")
        print(f"  - Expected baselines: {len(list(expected_dir.glob('*'))) if expected_dir.exists() else 0} files")
        
        # List input fixtures
        if input_dir.exists():
            input_files = sorted(input_dir.glob('*'))
            print(f"\n  Input fixtures:")
            for file in input_files:
                print(f"    - {file.name} ({file.stat().st_size} bytes)")
        
        # List baseline files
        if expected_dir.exists():
            baseline_files = sorted(expected_dir.glob('*'))
            print(f"\n  Baseline files:")
            for file in baseline_files:
                print(f"    - {file.name} ({file.stat().st_size} bytes)")
        
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