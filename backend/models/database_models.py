import datetime
from sqlalchemy import Column, String, Float, DateTime, Text, JSON, Boolean
from database import Base

class AnalysisRecord(Base):
    __tablename__ = "analyses"

    id = Column(String, primary_key=True, index=True)
    filename = Column(String, nullable=False)
    original_filename = Column(String, nullable=False)
    file_path = Column(String, nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.datetime.now(datetime.timezone.utc))
    status = Column(String, default="pending", index=True)
    current_step = Column(String, default="Uploaded")
    
    # Decision Engine Outputs
    overall_score = Column(Float, nullable=True)
    authenticity_status = Column(String, nullable=True)
    ai_probability = Column(Float, nullable=True)
    confidence = Column(String, nullable=True)
    extracted_text = Column(Text, nullable=True)
    final_summary = Column(Text, nullable=True)
    
    # Structured JSON stores for deep forensic breakdown
    evidence_bullets = Column(JSON, nullable=True)
    score_breakdown = Column(JSON, nullable=True)
    modules_results = Column(JSON, nullable=True)
    artifacts = Column(JSON, nullable=True)
    
    # Metadata flags
    is_demo = Column(Boolean, default=False)
    error_message = Column(Text, nullable=True)
