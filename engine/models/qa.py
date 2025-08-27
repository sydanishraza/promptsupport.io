from pydantic import BaseModel
from typing import List, Optional

class QAFlag(BaseModel):
    code: str            # e.g., P0_UNSUPPORTED_CLAIM
    severity: str        # P0|P1
    message: str
    location: Optional[str] = None

class QAReport(BaseModel):
    job_id: str
    coverage_percent: float
    flags: List[QAFlag]
    broken_links: List[str] = []
    missing_media: List[str] = []