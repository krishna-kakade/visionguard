from pydantic import BaseModel, ConfigDict
from typing import Optional, Dict, Any, List
from datetime import datetime

class AnalysisStatusResponse(BaseModel):
    id: str
    status: str
    current_step: str
    error_message: Optional[str] = None

class AnalysisDetailResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    filename: str
    original_filename: str
    created_at: datetime
    status: str
    current_step: str
    overall_score: Optional[float] = None
    authenticity_status: Optional[str] = None
    ai_probability: Optional[float] = None
    confidence: Optional[str] = None
    extracted_text: Optional[str] = None
    final_summary: Optional[str] = None
    evidence_bullets: Optional[List[str]] = None
    score_breakdown: Optional[Dict[str, Any]] = None
    modules_results: Optional[Dict[str, Any]] = None
    artifacts: Optional[Dict[str, str]] = None
    is_demo: bool = False
    error_message: Optional[str] = None

AnalysisResponse = AnalysisDetailResponse
