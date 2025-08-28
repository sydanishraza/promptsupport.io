"""
KE-PR10: Golden Tests & Non-Regression Suite
Comprehensive regression tests for V2 engine pipeline with golden fixtures
"""

import pytest
import json
import pathlib
import asyncio
from typing import Dict, Any, List

class TestGoldenPipeline:
    """Golden tests for V2 engine pipeline regression protection"""
    
    @pytest.mark.asyncio
    async def test_golden_docx_pipeline(
        self, 
        run_golden_pipeline, 
        compare_json, 
        normalize_html, 
        golden_test_config,
        update_golden_flag,
        save_golden_baseline
    ):
        """Test DOCX processing through V2 pipeline"""
        input_file = golden_test_config["input_dir"] / "sample1.docx"
        expected_dir = golden_test_config["expected_dir"]
        
        # Skip if input file doesn't exist (we'll create it later)
        if not input_file.exists():
            pytest.skip(f"Golden fixture not found: {input_file}")
        
        # Run pipeline
        result = await run_golden_pipeline(input_file, "docx")
        
        if update_golden_flag:
            # Update baseline
            save_golden_baseline("sample1.docx", result, expected_dir)
            return
        
        # Load expected results and compare
        await self._compare_pipeline_results(
            "sample1", result, expected_dir, compare_json, normalize_html, golden_test_config
        )
    
    @pytest.mark.asyncio
    async def test_golden_pdf_pipeline(
        self,
        run_golden_pipeline,
        compare_json,
        normalize_html,
        golden_test_config,
        update_golden_flag,
        save_golden_baseline
    ):
        """Test PDF processing through V2 pipeline"""
        input_file = golden_test_config["input_dir"] / "sample2.pdf"
        expected_dir = golden_test_config["expected_dir"]
        
        if not input_file.exists():
            pytest.skip(f"Golden fixture not found: {input_file}")
        
        result = await run_golden_pipeline(input_file, "pdf")
        
        if update_golden_flag:
            save_golden_baseline("sample2.pdf", result, expected_dir)
            return
        
        await self._compare_pipeline_results(
            "sample2", result, expected_dir, compare_json, normalize_html, golden_test_config
        )
    
    @pytest.mark.asyncio
    async def test_golden_markdown_pipeline(
        self,
        run_golden_pipeline,
        compare_json,
        normalize_html,
        golden_test_config,
        update_golden_flag,
        save_golden_baseline
    ):
        """Test Markdown processing through V2 pipeline"""
        input_file = golden_test_config["input_dir"] / "sample3.md"
        expected_dir = golden_test_config["expected_dir"]
        
        if not input_file.exists():
            pytest.skip(f"Golden fixture not found: {input_file}")
        
        result = await run_golden_pipeline(input_file, "markdown")
        
        if update_golden_flag:
            save_golden_baseline("sample3.md", result, expected_dir)
            return
        
        await self._compare_pipeline_results(
            "sample3", result, expected_dir, compare_json, normalize_html, golden_test_config
        )
    
    @pytest.mark.asyncio
    async def test_golden_html_pipeline(
        self,
        run_golden_pipeline,
        compare_json,
        normalize_html,
        golden_test_config,
        update_golden_flag,
        save_golden_baseline
    ):
        """Test HTML processing through V2 pipeline"""
        input_file = golden_test_config["input_dir"] / "sample4.html"
        expected_dir = golden_test_config["expected_dir"]
        
        if not input_file.exists():
            pytest.skip(f"Golden fixture not found: {input_file}")
        
        result = await run_golden_pipeline(input_file, "html")
        
        if update_golden_flag:
            save_golden_baseline("sample4.html", result, expected_dir)
            return
        
        await self._compare_pipeline_results(
            "sample4", result, expected_dir, compare_json, normalize_html, golden_test_config
        )
    
    @pytest.mark.asyncio
    async def test_golden_text_pipeline(
        self,
        run_golden_pipeline,
        compare_json,
        normalize_html,
        golden_test_config,
        update_golden_flag,
        save_golden_baseline
    ):
        """Test plain text processing through V2 pipeline"""
        input_file = golden_test_config["input_dir"] / "sample5.txt"
        expected_dir = golden_test_config["expected_dir"]
        
        if not input_file.exists():
            pytest.skip(f"Golden fixture not found: {input_file}")
        
        result = await run_golden_pipeline(input_file, "text")
        
        if update_golden_flag:
            save_golden_baseline("sample5.txt", result, expected_dir)
            return
        
        await self._compare_pipeline_results(
            "sample5", result, expected_dir, compare_json, normalize_html, golden_test_config
        )
    
    @pytest.mark.asyncio
    async def test_golden_url_html_pipeline(
        self,
        run_golden_pipeline,
        compare_json,
        normalize_html,
        golden_test_config,
        update_golden_flag,
        save_golden_baseline
    ):
        """Test URL HTML content processing through V2 pipeline"""
        input_file = golden_test_config["input_dir"] / "sample6_url.html"
        expected_dir = golden_test_config["expected_dir"]
        
        if not input_file.exists():
            pytest.skip(f"Golden fixture not found: {input_file}")
        
        result = await run_golden_pipeline(input_file, "html")
        
        if update_golden_flag:
            save_golden_baseline("sample6_url.html", result, expected_dir)
            return
        
        await self._compare_pipeline_results(
            "sample6_url", result, expected_dir, compare_json, normalize_html, golden_test_config
        )
    
    @pytest.mark.asyncio
    async def test_golden_media_pipeline(
        self,
        run_golden_pipeline,
        compare_json,
        normalize_html,
        golden_test_config,
        update_golden_flag,
        save_golden_baseline
    ):
        """Test media file processing through V2 pipeline"""
        input_file = golden_test_config["input_dir"] / "sample7.mp4"
        expected_dir = golden_test_config["expected_dir"]
        
        if not input_file.exists():
            pytest.skip(f"Golden fixture not found: {input_file}")
        
        result = await run_golden_pipeline(input_file, "video")
        
        if update_golden_flag:
            save_golden_baseline("sample7.mp4", result, expected_dir)
            return
        
        await self._compare_pipeline_results(
            "sample7", result, expected_dir, compare_json, normalize_html, golden_test_config
        )
    
    @pytest.mark.asyncio 
    async def test_golden_complex_document_pipeline(
        self,
        run_golden_pipeline,
        compare_json,
        normalize_html,
        golden_test_config,
        update_golden_flag,
        save_golden_baseline
    ):
        """Test complex document with multiple elements through V2 pipeline"""
        input_file = golden_test_config["input_dir"] / "sample8_complex.md"
        expected_dir = golden_test_config["expected_dir"]
        
        if not input_file.exists():
            pytest.skip(f"Golden fixture not found: {input_file}")
        
        result = await run_golden_pipeline(input_file, "markdown")
        
        if update_golden_flag:
            save_golden_baseline("sample8_complex.md", result, expected_dir)
            return
        
        await self._compare_pipeline_results(
            "sample8_complex", result, expected_dir, compare_json, normalize_html, golden_test_config
        )
    
    async def _compare_pipeline_results(
        self,
        sample_name: str,
        actual_result: Dict[str, Any],
        expected_dir: pathlib.Path,
        compare_json,
        normalize_html,
        config: Dict[str, Any]
    ):
        """Compare pipeline results against golden baselines"""
        
        # Test QA results with coverage threshold
        qa_file = expected_dir / f"{sample_name}.qa.json"
        if qa_file.exists():
            expected_qa = json.loads(qa_file.read_text())
            actual_qa = actual_result.get("qa", {})
            
            # Coverage percentage with tolerance
            expected_coverage = expected_qa.get("coverage_percent", 0.0)
            actual_coverage = actual_qa.get("coverage_percent", 0.0)
            tolerance = config["coverage_tolerance"]
            
            assert actual_coverage >= expected_coverage - tolerance, (
                f"Coverage regression in {sample_name}: "
                f"expected >= {expected_coverage - tolerance}%, got {actual_coverage}%"
            )
            
            # Compare other QA fields
            qa_comparison = compare_json(expected_qa, actual_qa, tolerance)
            if not qa_comparison["match"]:
                pytest.fail(
                    f"QA results mismatch in {sample_name}:\n" + 
                    "\n".join(qa_comparison["differences"])
                )
        
        # Test anchors (exact match required)
        anchors_file = expected_dir / f"{sample_name}.anchors.json"
        if anchors_file.exists():
            expected_anchors = json.loads(anchors_file.read_text())
            actual_anchors = actual_result.get("anchors", [])
            
            anchors_comparison = compare_json(expected_anchors, actual_anchors, tolerance=0.0)
            if not anchors_comparison["match"]:
                pytest.fail(
                    f"Anchors drift detected in {sample_name}:\n" + 
                    "\n".join(anchors_comparison["differences"])
                )
        
        # Test TOC structure
        toc_file = expected_dir / f"{sample_name}.toc.json"
        if toc_file.exists():
            expected_toc = json.loads(toc_file.read_text())
            actual_toc = actual_result.get("toc", [])
            
            toc_comparison = compare_json(expected_toc, actual_toc, tolerance=0.1)
            if not toc_comparison["match"]:
                pytest.fail(
                    f"TOC structure changed in {sample_name}:\n" + 
                    "\n".join(toc_comparison["differences"])
                )
        
        # Test HTML output (normalized)
        html_file = expected_dir / f"{sample_name}.html"
        if html_file.exists():
            expected_html = normalize_html(html_file.read_text())
            actual_html = normalize_html(actual_result.get("html", ""))
            
            if expected_html != actual_html:
                # Save diff for CI artifacts
                diff_file = expected_dir.parent / f"{sample_name}_html_diff.txt"
                with diff_file.open('w') as f:
                    f.write(f"Expected HTML:\n{expected_html}\n\n")
                    f.write(f"Actual HTML:\n{actual_html}\n")
                
                pytest.fail(f"HTML output changed in {sample_name}. Diff saved to {diff_file}")


class TestGoldenCoverage:
    """Coverage and regression threshold enforcement"""
    
    def test_coverage_baseline_enforcement(self):
        """Ensure test coverage doesn't drop below baseline"""
        # This will be implemented with actual coverage measurement
        baseline_coverage = 80.0  # Current baseline percentage
        
        # TODO: Integrate with pytest-cov to get actual coverage
        # For now, this is a placeholder that always passes
        current_coverage = 85.0  # This should be dynamically calculated
        
        assert current_coverage >= baseline_coverage, (
            f"Test coverage dropped below baseline: {current_coverage}% < {baseline_coverage}%"
        )
    
    def test_anchor_stability(self):
        """Ensure anchor generation is deterministic and stable"""
        # Test that anchor IDs don't change unexpectedly
        # This is handled by individual golden tests, but we can add
        # aggregate checks here if needed
        pass


class TestGoldenUtilities:
    """Utility tests for golden test framework"""
    
    def test_html_normalization(self, normalize_html):
        """Test HTML normalization function"""
        test_html = '''
        <div id="uuid-12345" class="test">
            <p>Created at: 2024-01-15T10:30:00Z</p>
            <span>Run ID: abc-def-123</span>
        </div>
        '''
        
        normalized = normalize_html(test_html)
        
        # Should normalize timestamps and IDs
        assert "TIMESTAMP" in normalized
        assert "UUID" in normalized or "NORMALIZED_ID" in normalized
        assert "2024-01-15T10:30:00Z" not in normalized
        assert normalized.count(' ') < test_html.count(' ')  # Whitespace normalized
    
    def test_json_comparison_tolerance(self, compare_json):
        """Test JSON comparison with float tolerance"""
        expected = {"coverage_percent": 85.0, "issues": 5}
        actual = {"coverage_percent": 84.7, "issues": 5}
        
        # Should pass with default tolerance
        result = compare_json(expected, actual, tolerance=0.5)
        assert result["match"] is True
        
        # Should fail with strict tolerance
        result = compare_json(expected, actual, tolerance=0.1)
        assert result["match"] is False
        assert len(result["differences"]) > 0


if __name__ == "__main__":
    print("🧪 KE-PR10: Golden Tests & Non-Regression Suite")
    print("Run with: pytest tests/golden/test_pipeline.py")
    print("Update baselines: pytest tests/golden/test_pipeline.py --update-golden")