"""
KE-PR5: V2 Pipeline Orchestrator
Coordinates all V2 stages with typed I/O and comprehensive logging
"""

import uuid
import time
from datetime import datetime
from typing import Tuple, Dict, Any, List

# Import typed models from KE-PR1
from ..models.io import RawBundle, NormDoc, Section, SourceSpan
from ..models.qa import QAReport, QAFlag
from ..logging_util import stage_log, logger

# Import all V2 stage classes from KE-PR4
from .analyzer import V2MultiDimensionalAnalyzer
from .outline import V2GlobalOutlinePlanner, V2PerArticleOutlinePlanner
from .prewrite import V2PrewriteSystem
from .generator import V2ArticleGenerator
from .style import V2StyleProcessor
from .related import V2RelatedLinksSystem
from .gaps import V2GapFillingSystem
from .evidence import V2EvidenceTaggingSystem
from .code_norm import V2CodeNormalizationSystem
from .validators import validate as run_validators
from .crossqa import V2CrossArticleQASystem
from .adapt import V2AdaptiveAdjustmentSystem
from .publish import V2PublishingSystem
from .versioning import V2VersioningSystem
from .review import V2ReviewSystem
from .extractor import V2ContentExtractor


class Pipeline:
    """V2 Pipeline Orchestrator: Coordinates all V2 stages with typed I/O and comprehensive logging"""
    
    def __init__(self, llm_client=None, existing_v2_instances=None):
        """Initialize pipeline with all V2 stage instances"""
        self.llm = llm_client
        
        # Use existing V2 instances if provided (for integration with server.py globals)
        if existing_v2_instances:
            print("🔗 KE-PR5: Using existing V2 instances from server.py")
            self.extractor = existing_v2_instances.get('extractor', V2ContentExtractor())
            self.analyzer = existing_v2_instances.get('analyzer', V2MultiDimensionalAnalyzer())
            self.global_planner = existing_v2_instances.get('global_planner', V2GlobalOutlinePlanner())
            self.per_article_planner = existing_v2_instances.get('per_article_planner', V2PerArticleOutlinePlanner())
            self.prewrite_system = existing_v2_instances.get('prewrite_system', V2PrewriteSystem())
            self.generator = existing_v2_instances.get('generator', V2ArticleGenerator())
            self.style_processor = existing_v2_instances.get('style_processor', V2StyleProcessor())
            self.related_links = existing_v2_instances.get('related_links', V2RelatedLinksSystem())
            self.gap_filling = existing_v2_instances.get('gap_filling', V2GapFillingSystem())
            self.evidence_tagging = existing_v2_instances.get('evidence_tagging', V2EvidenceTaggingSystem())
            self.code_norm = existing_v2_instances.get('code_norm', V2CodeNormalizationSystem())
            # Note: validator now uses function-based approach from validators module
            self.cross_qa = existing_v2_instances.get('cross_qa', V2CrossArticleQASystem())
            self.adaptive_adjustment = existing_v2_instances.get('adaptive_adjustment', V2AdaptiveAdjustmentSystem())
            self.publisher = existing_v2_instances.get('publisher', V2PublishingSystem())
            self.versioning = existing_v2_instances.get('versioning', V2VersioningSystem())
            self.reviewer = existing_v2_instances.get('reviewer', V2ReviewSystem())
        else:
            # Initialize new V2 stage class instances
            self.extractor = V2ContentExtractor()
            self.analyzer = V2MultiDimensionalAnalyzer()
            self.global_planner = V2GlobalOutlinePlanner()
            self.per_article_planner = V2PerArticleOutlinePlanner()
            self.prewrite_system = V2PrewriteSystem()
            self.generator = V2ArticleGenerator()
            self.style_processor = V2StyleProcessor()
            self.related_links = V2RelatedLinksSystem()
            self.gap_filling = V2GapFillingSystem()
            self.evidence_tagging = V2EvidenceTaggingSystem()
            self.code_norm = V2CodeNormalizationSystem()
            # Note: validator now uses function-based approach from validators module
            self.cross_qa = V2CrossArticleQASystem()
            self.adaptive_adjustment = V2AdaptiveAdjustmentSystem()
            self.publisher = V2PublishingSystem()
            self.versioning = V2VersioningSystem()
            self.reviewer = V2ReviewSystem()
        
        print("🚀 KE-PR5: V2 Pipeline orchestrator initialized with 17 stages")

    @stage_log("v2_pipeline_complete")
    async def run(self, job_id: str, content: str, metadata: Dict[str, Any]) -> Tuple[List[Dict[str, Any]], QAReport, str]:
        """
        Run the complete V2 pipeline orchestration
        
        Args:
            job_id: Unique job identifier
            content: Raw content to process
            metadata: Content metadata (title, type, etc.)
        
        Returns:
            Tuple of (articles, qa_report, version_id)
        """
        try:
            pipeline_start = time.time()
            run_id = f"run_{int(datetime.utcnow().timestamp())}_{uuid.uuid4().hex[:8]}"
            
            print(f"🚀 KE-PR5: Starting V2 pipeline - job_id: {job_id}, run_id: {run_id}")
            
            # Stage 1: Content Extraction & Normalization
            normalized_doc = await self._stage_extract_content(content, metadata, run_id, job_id)
            
            # Stage 2: Multi-dimensional Analysis
            analysis_result = await self._stage_analyze(normalized_doc, run_id)
            analysis = analysis_result.get('analysis', {}) if analysis_result else {}
            
            # Stage 3: Global Outline Planning
            global_outline = await self._stage_global_outline(normalized_doc, analysis, run_id)
            
            # Stage 4: Per-Article Outline Planning  
            per_article_outlines = await self._stage_per_article_outline(normalized_doc, global_outline, analysis, run_id)
            
            # Stage 5: Section-Grounded Prewrite
            prewrite_result = await self._stage_prewrite(content, metadata, global_outline, per_article_outlines, analysis, run_id)
            
            # Stage 6: Article Generation
            generated_articles = await self._stage_generate_articles(normalized_doc, per_article_outlines, analysis, run_id)
            
            # Stage 7: Evidence Tagging
            articles = await self._stage_evidence_tagging(generated_articles, normalized_doc, prewrite_result, run_id)
            
            # Stage 8: Style Processing
            articles = await self._stage_style_processing(content, metadata, articles, generated_articles, analysis, run_id)
            
            # Stage 9: Related Links Generation
            articles = await self._stage_related_links(articles, content, normalized_doc, run_id)
            
            # Stage 10: Gap Filling
            articles = await self._stage_gap_filling(articles, content, normalized_doc, run_id)
            
            # Stage 11: Code Normalization
            articles = await self._stage_code_normalization(articles, normalized_doc, prewrite_result, run_id)
            
            # Stage 12: Validation
            validation_result = await self._stage_validation(normalized_doc, generated_articles, analysis, run_id)
            
            # Stage 13: Cross-Article QA
            qa_result = await self._stage_cross_qa(generated_articles, run_id)
            
            # Stage 14: Adaptive Adjustment
            adjustment_result = await self._stage_adaptive_adjustment(generated_articles, analysis, run_id)
            
            # Stage 15: Publishing
            publishing_result = await self._stage_publishing(articles, generated_articles, validation_result, qa_result, adjustment_result, run_id)
            
            # Stage 16: Versioning
            version_id = await self._stage_versioning(articles, publishing_result, run_id)
            
            # Stage 17: Review Queue
            await self._stage_review(version_id, qa_result, run_id)
            
            # Create QA Report
            qa_report = self._create_qa_report(job_id, validation_result, qa_result, adjustment_result)
            
            # Log pipeline completion
            pipeline_duration = (time.time() - pipeline_start) * 1000
            print(f"✅ KE-PR5: V2 pipeline complete - {len(articles)} articles, duration: {pipeline_duration:.0f}ms")
            
            return articles, qa_report, version_id
            
        except Exception as e:
            print(f"❌ KE-PR5: V2 pipeline failed - {e}")
            # Return empty results on failure
            empty_qa = QAReport(job_id=job_id, coverage_percent=0.0, flags=[
                QAFlag(code="P0_PIPELINE_ERROR", severity="P0", message=str(e))
            ])
            return [], empty_qa, f"error_{job_id}"

    @stage_log("extract_content")
    async def _stage_extract_content(self, content: str, metadata: Dict[str, Any], run_id: str, job_id: str):
        """Stage 1: Content Extraction & Normalization"""
        print(f"📄 KE-PR5: Stage 1 - Content extraction - {len(content)} chars - job_id: {job_id}")
        
        title = metadata.get('title', metadata.get('original_filename', 'Text Content'))
        normalized_doc = await self.extractor.extract_raw_text(content, title, job_id)
        
        print(f"✅ KE-PR5: Stage 1 complete - {len(normalized_doc.blocks)} blocks extracted - job_id: {job_id}")
        return normalized_doc

    @stage_log("analyze")
    async def _stage_analyze(self, normalized_doc, run_id: str):
        """Stage 2: Multi-dimensional Analysis"""
        print(f"🔍 KE-PR5: Stage 2 - Multi-dimensional analysis")
        
        analysis_result = await self.analyzer.analyze_normalized_document(normalized_doc, run_id)
        analysis = analysis_result.get('analysis', {}) if analysis_result else {}
        
        print(f"✅ KE-PR5: Stage 2 complete - {analysis.get('content_type', 'unknown')} content, {analysis.get('granularity', 'unknown')} granularity")
        return analysis_result

    @stage_log("global_outline")
    async def _stage_global_outline(self, normalized_doc, analysis: Dict[str, Any], run_id: str):
        """Stage 3: Global Outline Planning"""
        print(f"📋 KE-PR5: Stage 3 - Global outline planning")
        
        # Note: Method signature may need adjustment when actual implementation is moved
        global_outline = await self.global_planner.create_global_outline(normalized_doc, analysis, run_id)
        outline = global_outline.get('outline', {}) if global_outline else {}
        
        article_count = len(outline.get('articles', []))
        print(f"✅ KE-PR5: Stage 3 complete - {article_count} articles planned")
        return global_outline

    @stage_log("per_article_outline")
    async def _stage_per_article_outline(self, normalized_doc, global_outline: Dict[str, Any], analysis: Dict[str, Any], run_id: str):
        """Stage 4: Per-Article Outline Planning"""
        print(f"📝 KE-PR5: Stage 4 - Per-article outline planning")
        
        outline = global_outline.get('outline', {}) if global_outline else {}
        per_article_outlines = await self.per_article_planner.create_per_article_outlines(
            normalized_doc, outline, analysis, run_id
        )
        
        outline_count = len(per_article_outlines.get('per_article_outlines', []))
        print(f"✅ KE-PR5: Stage 4 complete - {outline_count} detailed outlines created")
        return per_article_outlines

    @stage_log("prewrite")
    async def _stage_prewrite(self, content: str, metadata: Dict[str, Any], global_outline: Dict[str, Any], per_article_outlines: Dict[str, Any], analysis: Dict[str, Any], run_id: str):
        """Stage 5: Section-Grounded Prewrite"""
        print(f"📚 KE-PR5: Stage 5 - Section-grounded prewrite")
        
        outline = global_outline.get('outline', {}) if global_outline else {}
        article_outlines = outline.get('articles', [])
        
        prewrite_result = await self.prewrite_system.execute_prewrite_pass(
            content, metadata.get('content_type', 'text'), article_outlines,
            per_article_outlines.get('per_article_outlines', {}), analysis, run_id
        )
        
        success_count = prewrite_result.get('successful_prewrites', 0)
        print(f"✅ KE-PR5: Stage 5 complete - {success_count} prewrites successful")
        return prewrite_result

    @stage_log("generate_articles")
    async def _stage_generate_articles(self, normalized_doc, per_article_outlines: Dict[str, Any], analysis: Dict[str, Any], run_id: str):
        """Stage 6: Article Generation"""
        print(f"✍️ KE-PR5: Stage 6 - Article generation")
        
        outlines = per_article_outlines.get('per_article_outlines', [])
        generated_articles = await self.generator.generate_final_articles(
            normalized_doc, outlines, analysis, run_id
        )
        
        article_count = len(generated_articles.get('generated_articles', []))
        print(f"✅ KE-PR5: Stage 6 complete - {article_count} articles generated")
        return generated_articles

    @stage_log("evidence_tagging")
    async def _stage_evidence_tagging(self, generated_articles: Dict[str, Any], normalized_doc, prewrite_result: Dict[str, Any], run_id: str):
        """Stage 7: Evidence Tagging"""
        print(f"🏷️ KE-PR5: Stage 7 - Evidence tagging")
        
        # Convert generated articles to expected format
        articles = self._convert_generated_to_articles(generated_articles, normalized_doc, run_id)
        
        evidence_result = await self.evidence_tagging.tag_content_with_evidence(
            articles, normalized_doc.blocks, prewrite_result, run_id
        )
        
        tagged_count = evidence_result.get('tagged_paragraphs', 0)
        print(f"✅ KE-PR5: Stage 7 complete - {tagged_count} paragraphs tagged with evidence")
        return articles

    @stage_log("style_processing")
    async def _stage_style_processing(self, content: str, metadata: Dict[str, Any], articles: List[Dict[str, Any]], generated_articles: Dict[str, Any], analysis: Dict[str, Any], run_id: str):
        """Stage 8: Style Processing"""
        print(f"🎨 KE-PR5: Stage 8 - Woolf-aligned style processing")
        
        style_result = await self.style_processor.apply_style_formatting(
            content, metadata.get('content_type', 'text'), articles,
            generated_articles, analysis, run_id
        )
        
        # Apply formatted content to articles
        style_results = style_result.get('style_results', [])
        for i, article in enumerate(articles):
            article_style_result = next((r for r in style_results if r.get('article_index') == i), None)
            if article_style_result and article_style_result.get('style_status') == 'success':
                formatted_content = article_style_result.get('formatted_content', '')
                if formatted_content and len(formatted_content) > 100:
                    article['content'] = formatted_content
                    article['formatted_content'] = formatted_content
        
        success_count = style_result.get('successful_formatting', 0)
        print(f"✅ KE-PR5: Stage 8 complete - {success_count} articles styled")
        return articles

    @stage_log("related_links")
    async def _stage_related_links(self, articles: List[Dict[str, Any]], content: str, normalized_doc, run_id: str):
        """Stage 9: Related Links Generation"""
        print(f"🔗 KE-PR5: Stage 9 - Related links generation")
        
        links_added = 0
        for article in articles:
            related_result = await self.related_links.generate_related_links(
                article, content, normalized_doc.blocks, run_id
            )
            
            if related_result.get('related_links_status') == 'success':
                article['related_links'] = related_result.get('related_links', [])
                article['related_links_count'] = len(article['related_links'])
                links_added += len(article['related_links'])
        
        print(f"✅ KE-PR5: Stage 9 complete - {links_added} related links generated")
        return articles

    @stage_log("gap_filling")
    async def _stage_gap_filling(self, articles: List[Dict[str, Any]], content: str, normalized_doc, run_id: str):
        """Stage 10: Gap Filling"""
        print(f"🔍 KE-PR5: Stage 10 - Intelligent gap filling")
        
        gap_result = await self.gap_filling.fill_content_gaps(
            articles, content, normalized_doc.blocks, run_id, enrich_mode="internal"
        )
        
        gaps_filled = gap_result.get('total_gaps_filled', 0)
        print(f"✅ KE-PR5: Stage 10 complete - {gaps_filled} gaps filled")
        return articles

    @stage_log("code_normalization")
    async def _stage_code_normalization(self, articles: List[Dict[str, Any]], normalized_doc, prewrite_result: Dict[str, Any], run_id: str):
        """Stage 11: Code Normalization"""
        print(f"💻 KE-PR5: Stage 11 - Code block normalization")
        
        code_result = await self.code_norm.normalize_code_blocks(
            articles, normalized_doc.blocks, prewrite_result, run_id
        )
        
        normalized_count = code_result.get('normalized_blocks', 0)
        print(f"✅ KE-PR5: Stage 11 complete - {normalized_count} code blocks normalized")
        return articles

    @stage_log("validation")
    async def _stage_validation(self, normalized_doc, generated_articles: Dict[str, Any], analysis: Dict[str, Any], run_id: str):
        """Stage 12: Validation"""
        print(f"🔍 KE-PR5: Stage 12 - Comprehensive validation")
        
        # Use new validators module function-based approach
        qa_report = run_validators(normalized_doc)
        
        # Persist QA report to database (KE-PR7)
        try:
            # Import persist function here to avoid circular imports
            import sys
            import os
            backend_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'backend')
            if backend_path not in sys.path:
                sys.path.append(backend_path)
            
            from server import persist_qa_report
            await persist_qa_report(qa_report, run_id)
        except Exception as e:
            print(f"⚠️ KE-PR7: Could not persist QA report - {e}")
        
        # Convert QAReport to validation result format for compatibility
        validation_result = {
            'validation_status': 'passed' if qa_report.coverage_percent >= 70.0 and len([f for f in qa_report.flags if f.severity == "P0"]) == 0 else 'issues_found',
            'qa_report': qa_report,
            'coverage_percent': qa_report.coverage_percent,
            'total_flags': len(qa_report.flags),
            'p0_flags': len([f for f in qa_report.flags if f.severity == "P0"]),
            'p1_flags': len([f for f in qa_report.flags if f.severity == "P1"]),
            'broken_links': qa_report.broken_links,
            'missing_media': qa_report.missing_media,
            'run_id': run_id
        }
        
        status = validation_result.get('validation_status', 'unknown')
        print(f"✅ KE-PR5: Stage 12 complete - validation status: {status}")
        return validation_result

    @stage_log("cross_qa")
    async def _stage_cross_qa(self, generated_articles: Dict[str, Any], run_id: str):
        """Stage 13: Cross-Article QA"""
        print(f"🔍 KE-PR5: Stage 13 - Cross-article quality assurance")
        
        qa_result = await self.cross_qa.perform_cross_article_qa(generated_articles, run_id)
        
        issues_found = qa_result.get('summary', {}).get('issues_found', 0)
        print(f"✅ KE-PR5: Stage 13 complete - {issues_found} issues found")
        return qa_result

    @stage_log("adaptive_adjustment")
    async def _stage_adaptive_adjustment(self, generated_articles: Dict[str, Any], analysis: Dict[str, Any], run_id: str):
        """Stage 14: Adaptive Adjustment"""
        print(f"⚖️ KE-PR5: Stage 14 - Adaptive adjustment")
        
        adjustment_result = await self.adaptive_adjustment.perform_adaptive_adjustment(
            generated_articles, analysis, run_id
        )
        
        adjustments = adjustment_result.get('adjustment_summary', {}).get('total_adjustments', 0)
        print(f"✅ KE-PR5: Stage 14 complete - {adjustments} adjustments made")
        return adjustment_result

    @stage_log("publishing")
    async def _stage_publishing(self, articles: List[Dict[str, Any]], generated_articles: Dict[str, Any], validation_result: Dict[str, Any], qa_result: Dict[str, Any], adjustment_result: Dict[str, Any], run_id: str):
        """Stage 15: Publishing"""
        print(f"📚 KE-PR5: Stage 15 - Publishing")
        
        publishing_result = await self.publisher.publish_v2_content(
            articles, generated_articles, validation_result, qa_result, adjustment_result, run_id
        )
        
        published_count = publishing_result.get('published_articles', 0)
        print(f"✅ KE-PR5: Stage 15 complete - {published_count} articles published")
        return publishing_result

    @stage_log("versioning")
    async def _stage_versioning(self, articles: List[Dict[str, Any]], publishing_result: Dict[str, Any], run_id: str):
        """Stage 16: Versioning"""
        print(f"📦 KE-PR5: Stage 16 - Versioning")
        
        version_result = await self.versioning.create_version_from_articles(articles, run_id)
        version_id = version_result.get('version_id', f"v_{run_id}")
        
        print(f"✅ KE-PR5: Stage 16 complete - version created: {version_id}")
        return version_id

    @stage_log("review")
    async def _stage_review(self, version_id: str, qa_result: Dict[str, Any], run_id: str):
        """Stage 17: Review Queue"""
        print(f"👥 KE-PR5: Stage 17 - Review queue")
        
        review_result = await self.reviewer.enqueue_for_review(version_id, qa_result, run_id)
        
        review_id = review_result.get('review_id', 'none')
        print(f"✅ KE-PR5: Stage 17 complete - review queued: {review_id}")
        return review_result

    def _convert_generated_to_articles(self, generated_articles: Dict[str, Any], normalized_doc, run_id: str) -> List[Dict[str, Any]]:
        """Convert generated articles format to articles list format"""
        articles = []
        
        if generated_articles and 'generated_articles' in generated_articles:
            for generated_article in generated_articles['generated_articles']:
                article_data = generated_article.get('article_data', {})
                if article_data:
                    article_title = article_data.get('title', generated_article.get('article_id', 'Generated Article'))
                    
                    article = {
                        "id": str(uuid.uuid4()),
                        "title": article_title,
                        "content": article_data.get('html', ''),
                        "summary": article_data.get('summary', ''),
                        "status": "draft",
                        "created_at": datetime.utcnow().isoformat(),
                        "updated_at": datetime.utcnow().isoformat(),
                        "source_content": f"V2 Engine processed content from {normalized_doc.title}",
                        "source_type": "v2_generated",
                        "markdown": article_data.get('markdown', ''),
                        "takeaways": [],
                        "metadata": {
                            "engine": "v2",
                            "processing_version": "2.0",
                            "normalized_doc_id": normalized_doc.doc_id,
                            "run_id": run_id,
                            "article_id": generated_article.get('article_id', 'unknown'),
                            "validation_metadata": article_data.get('validation_metadata', {}),
                            "generated_by": "v2_pipeline_orchestrator"
                        }
                    }
                    articles.append(article)
        
        return articles

    def _create_qa_report(self, job_id: str, validation_result: Dict[str, Any], qa_result: Dict[str, Any], adjustment_result: Dict[str, Any]) -> QAReport:
        """Create comprehensive QA report from stage results"""
        flags = []
        coverage_percent = 95.0  # Default high coverage
        
        # Add validation flags
        if validation_result.get('validation_status') != 'passed':
            flags.append(QAFlag(
                code="P1_VALIDATION_ISSUES",
                severity="P1", 
                message=f"Validation status: {validation_result.get('validation_status', 'unknown')}"
            ))
            coverage_percent -= 10
        
        # Add QA flags
        qa_issues = qa_result.get('summary', {}).get('issues_found', 0)
        if qa_issues > 0:
            flags.append(QAFlag(
                code="P1_QA_ISSUES",
                severity="P1",
                message=f"Cross-article QA found {qa_issues} issues"
            ))
            coverage_percent -= 5
        
        # Add adjustment flags
        adjustments = adjustment_result.get('adjustment_summary', {}).get('total_adjustments', 0)
        if adjustments > 5:
            flags.append(QAFlag(
                code="P0_EXCESSIVE_ADJUSTMENTS", 
                severity="P0",
                message=f"Excessive adjustments required: {adjustments}"
            ))
            coverage_percent -= 15
        
        return QAReport(
            job_id=job_id,
            coverage_percent=max(coverage_percent, 0.0),
            flags=flags
        )


# Global pipeline instance (will be initialized when imported)
pipeline_instance = None

def get_pipeline(llm_client=None, existing_v2_instances=None) -> Pipeline:
    """Get or create the global pipeline instance"""
    global pipeline_instance
    # Always recreate if existing instances are provided to ensure proper integration
    if existing_v2_instances is not None or pipeline_instance is None:
        pipeline_instance = Pipeline(llm_client, existing_v2_instances)
    return pipeline_instance