"""
Media processing modules.
Intelligent media analysis, classification, and asset management.
"""

from .intelligence import MediaIntelligenceService
from .legacy import LegacyMediaIntelligenceService

# Current active service
media_intelligence = MediaIntelligenceService()

__all__ = ["MediaIntelligenceService", "LegacyMediaIntelligenceService", "media_intelligence"]