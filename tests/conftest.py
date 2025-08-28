"""
KE-PR10: Golden Tests Pytest Configuration
Provides fixtures and utilities for golden test framework
"""

import pytest
import json
import pathlib
import asyncio
import os
import sys
import tempfile
import shutil
from datetime import datetime
from typing import Dict, Any, List, Optional

# Add backend to path for V2 pipeline imports
backend_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'backend')
if backend_path not in sys.path:
    sys.path.append(backend_path)

# Add app root to path
app_root = os.path.dirname(os.path.dirname(__file__))
if app_root not in sys.path:
    sys.path.insert(0, app_root)

@pytest.fixture(scope="session")
def golden_test_config():
    """Configuration for golden tests"""
    return {
        "input_dir": pathlib.Path(__file__).parent / "golden" / "input",
        "expected_dir": pathlib.Path(__file__).parent / "golden" / "expected",
        "coverage_tolerance": 0.5,  # Allow 0.5% drift in coverage percentages
        "update_golden": False  # Set to True to update baselines
    }

@pytest.fixture(scope="session")
def update_golden_flag(request):
    """Check if --update-golden flag was passed"""
    return request.config.getoption("--update-golden", False)

def pytest_addoption(parser):
    """Add custom pytest options"""
    parser.addoption(
        "--update-golden",
        action="store_true",
        default=False,
        help="Update golden baseline files with current outputs"
    )

@pytest.fixture
def normalize_html():
    """HTML normalization utility for stable comparisons"""
    import re
    
    def _normalize_html(html_content: str) -> str:
        """Normalize HTML content for comparison"""
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
    
    return _normalize_html

@pytest.fixture
def compare_json():
    """JSON comparison utility with tolerance for floats"""
    
    def _compare_json(expected: Dict[Any, Any], actual: Dict[Any, Any], tolerance: float = 0.5) -> Dict[str, Any]:
        """
        Compare JSON objects with tolerance for float values
        Returns comparison result with differences
        """
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
    
    return _compare_json

@pytest.fixture
async def run_golden_pipeline():
    """
    Core fixture that runs V2 pipeline on input files and returns structured results
    """
    
    async def _run_pipeline(input_path: pathlib.Path, content_type: str = "auto") -> Dict[str, Any]:
        """
        Run V2 pipeline on input file and return structured results
        
        Args:
            input_path: Path to input file
            content_type: Type of content (auto-detected if not specified)
            
        Returns:
            Dictionary with qa, anchors, toc, and html results
        """
        try:
            # Import V2 pipeline components
            from app.engine.v2.pipeline import Pipeline
            from app.engine.models.io import RawBundle, ProcessingMetadata
            
            # Determine content type if auto
            if content_type == "auto":
                suffix = input_path.suffix.lower()
                type_mapping = {
                    '.docx': 'docx',
                    '.pdf': 'pdf', 
                    '.md': 'markdown',
                    '.html': 'html',
                    '.txt': 'text',
                    '.mp4': 'video'
                }
                content_type = type_mapping.get(suffix, 'text')
            
            # Read file content
            if content_type == 'video':
                # For video files, create a placeholder
                content = f"Video file: {input_path.name}"
                file_data = input_path.read_bytes()
            else:
                content = input_path.read_text(encoding='utf-8', errors='ignore')
                file_data = None
            
            # Create RawBundle
            metadata = ProcessingMetadata(
                source_type=content_type,
                original_filename=input_path.name,
                processing_timestamp=datetime.utcnow(),
                job_id=f"golden_test_{input_path.stem}"
            )
            
            raw_bundle = RawBundle(
                content=content,
                metadata=metadata,
                chunks=[{
                    "content": content,
                    "metadata": {
                        "source_type": content_type,
                        "original_filename": input_path.name
                    }
                }]
            )
            
            # Run V2 pipeline
            pipeline = Pipeline()
            result = await pipeline.run(raw_bundle)
            
            # Extract structured results
            pipeline_result = {
                "qa": {
                    "coverage_percent": 85.0,  # Default values for now
                    "total_issues": 0,
                    "critical_issues": 0
                },
                "anchors": [],
                "toc": [],
                "html": content,
                "metadata": {
                    "source_file": str(input_path),
                    "content_type": content_type,
                    "processing_timestamp": datetime.utcnow().isoformat()
                }
            }
            
            # If pipeline returned structured results, use them
            if hasattr(result, 'articles') and result.articles:
                article = result.articles[0]
                
                # Extract QA information
                if hasattr(article, 'qa_report'):
                    pipeline_result["qa"] = article.qa_report
                
                # Extract anchors
                if hasattr(article, 'headings'):
                    pipeline_result["anchors"] = article.headings
                
                # Extract TOC
                if hasattr(article, 'toc'):
                    pipeline_result["toc"] = article.toc
                
                # Extract HTML
                if hasattr(article, 'html'):
                    pipeline_result["html"] = article.html
                elif hasattr(article, 'content'):
                    pipeline_result["html"] = article.content
            
            return pipeline_result
            
        except Exception as e:
            # Return minimal result structure on error
            return {
                "qa": {
                    "coverage_percent": 0.0,
                    "total_issues": 1,
                    "critical_issues": 1,
                    "error": str(e)
                },
                "anchors": [],
                "toc": [],
                "html": f"Error processing {input_path}: {str(e)}",
                "metadata": {
                    "source_file": str(input_path),
                    "error": str(e),
                    "processing_timestamp": datetime.utcnow().isoformat()
                }
            }
    
    return _run_pipeline

@pytest.fixture
def save_golden_baseline():
    """Utility to save golden baseline files"""
    
    def _save_baseline(input_name: str, pipeline_result: Dict[str, Any], expected_dir: pathlib.Path):
        """Save pipeline results as golden baseline files"""
        base_name = pathlib.Path(input_name).stem
        
        # Save each component
        components = ["qa", "anchors", "toc", "html"]
        
        for component in components:
            if component in pipeline_result:
                output_file = expected_dir / f"{base_name}.{component}.json"
                
                if component == "html":
                    # Save HTML as text file
                    html_file = expected_dir / f"{base_name}.html"
                    html_file.write_text(pipeline_result[component], encoding='utf-8')
                else:
                    # Save other components as JSON
                    with output_file.open('w', encoding='utf-8') as f:
                        json.dump(pipeline_result[component], f, indent=2, ensure_ascii=False)
        
        print(f"✅ Saved golden baseline for {input_name}")
    
    return _save_baseline

print("🧪 KE-PR10: Golden Tests pytest configuration loaded")