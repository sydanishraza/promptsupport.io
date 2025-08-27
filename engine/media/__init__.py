"""
Media processing modules.
Intelligent media analysis, classification, and asset management.
"""

from .intelligence import MediaIntelligenceService

try:
    from .legacy import MediaIntelligenceService as LegacyMediaIntelligenceService
except ImportError:
    # Create fallback class if legacy module has issues
    class LegacyMediaIntelligenceService:
        async def analyze_media_comprehensive(self, *args, **kwargs): return {}
        def create_enhanced_media_html(self, *args, **kwargs): return ""
        def generate_contextual_placement(self, *args, **kwargs): return {}

# Current active service
media_intelligence = MediaIntelligenceService()

__all__ = ["MediaIntelligenceService", "LegacyMediaIntelligenceService", "media_intelligence"]