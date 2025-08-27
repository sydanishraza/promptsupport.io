"""
V2 engine modules.
Advanced content processing pipeline for PromptSupport V2+ generation.
"""

# Core pipeline classes
from .analyzer import V2MultiDimensionalAnalyzer
from .outline import V2GlobalOutlinePlanner, V2PerArticleOutlinePlanner
from .prewrite import V2PrewriteSystem
from .style import V2StyleProcessor
from .related import V2RelatedLinksSystem
from .gaps import V2GapFillingSystem
from .evidence import V2EvidenceTaggingSystem
from .code_norm import V2CodeNormalizationSystem
from .generator import V2ArticleGenerator
from .validate import V2ValidationSystem
from .crossqa import V2CrossArticleQASystem
from .adapt import V2AdaptiveAdjustmentSystem
from .publish import V2PublishingSystem
from .versioning import V2VersioningSystem
from .review import V2ReviewSystem
from .extractor import V2ContentExtractor
from .media import V2MediaManager

__all__ = [
    "V2MultiDimensionalAnalyzer",
    "V2GlobalOutlinePlanner", "V2PerArticleOutlinePlanner", 
    "V2PrewriteSystem",
    "V2StyleProcessor",
    "V2RelatedLinksSystem",
    "V2GapFillingSystem", 
    "V2EvidenceTaggingSystem",
    "V2CodeNormalizationSystem",
    "V2ArticleGenerator",
    "V2ValidationSystem",
    "V2CrossArticleQASystem",
    "V2AdaptiveAdjustmentSystem",
    "V2PublishingSystem",
    "V2VersioningSystem",
    "V2ReviewSystem",
    "V2ContentExtractor",
    "V2MediaManager"
]