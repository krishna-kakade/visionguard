"""Analysis endpoints for VisionGuard."""

import uuid
import shutil
from pathlib import Path
from typing import Optional
from fastapi import APIRouter, Depends, UploadFile, File, HTTPException, BackgroundTasks, Query
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from config import UPLOADS_DIR, RESULTS_DIR, REPORTS_DIR, ALLOWED_EXTENSIONS, ALLOWED_MIME_TYPES, MAX_UPLOAD_SIZE_BYTES
from database import get_db, SessionLocal
from models.database_models import AnalysisRecord
from schemas.analysis_schema import AnalysisStatusResponse, AnalysisDetailResponse
from services.analysis_pipeline import run_analysis_pipeline
from modules.preprocessing import validate_image_file

router = APIRouter(prefix="/api", tags=["Analysis"])


def run_pipeline_task(analysis_id: str, file_path: str, original_filename: str):
    """Background task runner with dedicated database session."""
    db = SessionLocal()
    try:
        run_analysis_pipeline(analysis_id, file_path, original_filename, db)
    finally:
        db.close()


@router.post("/analyze", response_model=AnalysisStatusResponse)
async def analyze_image(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """Uploads an image, validates format/integrity, and starts asynchronous forensic pipeline."""
    # 1. Validate file extension
    original_filename = file.filename or "uploaded_image.png"
    ext = Path(original_filename).suffix.lower()
    
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file type '{ext}'. Allowed extensions: {', '.join(sorted(ALLOWED_EXTENSIONS))}"
        )

    # 2. Validate MIME type
    if file.content_type and file.content_type.lower() not in ALLOWED_MIME_TYPES:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid MIME type '{file.content_type}'. Must be a supported image format."
        )

    # 3. Generate safe unique filename
    analysis_id = str(uuid.uuid4())
    safe_filename = f"{analysis_id}{ext}"
    target_path = UPLOADS_DIR / safe_filename

    # 4. Stream write and check file size
    bytes_read = 0
    with open(target_path, "wb") as buffer:
        while chunk := await file.read(1024 * 1024):  # 1MB chunks
            bytes_read += len(chunk)
            if bytes_read > MAX_UPLOAD_SIZE_BYTES:
                buffer.close()
                if target_path.exists():
                    target_path.unlink()
                raise HTTPException(
                    status_code=413,
                    detail=f"File exceeds maximum allowed size limit of {MAX_UPLOAD_SIZE_BYTES // (1024*1024)}MB."
                )
            buffer.write(chunk)

    # 5. Image readability check
    is_valid, err_msg = validate_image_file(target_path)
    if not is_valid:
        if target_path.exists():
            target_path.unlink()
        raise HTTPException(status_code=400, detail=f"Image could not be read: {err_msg}")

    # 6. Initialize database record
    record = AnalysisRecord(
        id=analysis_id,
        filename=safe_filename,
        original_filename=original_filename,
        file_path=str(target_path),
        status="processing",
        current_step="Image uploaded and validated",
        is_demo=False
    )
    db.add(record)
    db.commit()
    db.refresh(record)

    # 7. Dispatch pipeline to background
    background_tasks.add_task(run_pipeline_task, analysis_id, str(target_path), original_filename)

    return AnalysisStatusResponse(
        id=analysis_id,
        status="processing",
        current_step="Queued for analysis"
    )


@router.get("/analysis/{analysis_id}/status", response_model=AnalysisStatusResponse)
def get_analysis_status(analysis_id: str, db: Session = Depends(get_db)):
    """Pollable endpoint for tracking ongoing pipeline execution step."""
    record = db.query(AnalysisRecord).filter(AnalysisRecord.id == analysis_id).first()
    if not record:
        raise HTTPException(status_code=404, detail="Analysis record not found.")

    return AnalysisStatusResponse(
        id=record.id,
        status=record.status,
        current_step=record.current_step,
        error_message=record.error_message
    )


@router.get("/analysis/{analysis_id}", response_model=AnalysisDetailResponse)
def get_analysis_details(analysis_id: str, db: Session = Depends(get_db)):
    """Retrieves full multimodal analysis report and forensic metrics."""
    record = db.query(AnalysisRecord).filter(AnalysisRecord.id == analysis_id).first()
    if not record:
        raise HTTPException(status_code=404, detail="Analysis record not found.")

    return record


@router.get("/analysis/{analysis_id}/artifact/{filename}")
def get_analysis_artifact(analysis_id: str, filename: str, db: Session = Depends(get_db)):
    """Serves forensic visual artifacts (ELA, FFT spectrum, Copy-Move, Annotated OCR)."""
    # Check in results dir
    file_path = RESULTS_DIR / analysis_id / filename
    if not file_path.exists():
        # Check in uploads
        file_path = UPLOADS_DIR / filename
        if not file_path.exists():
            raise HTTPException(status_code=404, detail="Forensic artifact not found.")

    ext = file_path.suffix.lower()
    media_type = "image/png" if ext == ".png" else ("image/jpeg" if ext in [".jpg", ".jpeg"] else "image/webp")
    return FileResponse(path=str(file_path), media_type=media_type)


@router.get("/analysis/{analysis_id}/report")
def download_report(
    analysis_id: str,
    format: str = Query("pdf", pattern="^(pdf|json)$"),
    db: Session = Depends(get_db)
):
    """Exports structured forensic report as PDF or JSON."""
    record = db.query(AnalysisRecord).filter(AnalysisRecord.id == analysis_id).first()
    if not record:
        raise HTTPException(status_code=404, detail="Analysis record not found.")

    if format == "json":
        json_file = REPORTS_DIR / f"{analysis_id}.json"
        if not json_file.exists():
            raise HTTPException(status_code=404, detail="JSON report not found.")
        return FileResponse(
            path=str(json_file),
            filename=f"VisionGuard_Report_{analysis_id[:8]}.json",
            media_type="application/json"
        )
    else:
        pdf_file = REPORTS_DIR / f"{analysis_id}.pdf"
        if not pdf_file.exists():
            raise HTTPException(status_code=404, detail="PDF report not found.")
        return FileResponse(
            path=str(pdf_file),
            filename=f"VisionGuard_Report_{analysis_id[:8]}.pdf",
            media_type="application/pdf"
        )


@router.post("/demo", response_model=AnalysisDetailResponse)
def trigger_demo_mode(db: Session = Depends(get_db)):
    """Rule 48: Creates a clearly labeled DEMO RESULT with sample precomputed metrics."""
    demo_id = f"demo-{uuid.uuid4().hex[:8]}"
    
    demo_record = AnalysisRecord(
        id=demo_id,
        filename="sample_demo_investigation.jpg",
        original_filename="sample_demo_investigation.jpg",
        file_path="",
        status="completed",
        current_step="Completed",
        overall_score=42.0,
        authenticity_status="Potentially Suspicious",
        ai_probability=0.72,
        confidence="Medium",
        extracted_text="BREAKING: Official statement confirmed moon landing was staged in Hollywood desert studio.",
        final_summary="[DEMO RESULT] VisionGuard flagged this image as 'Potentially Suspicious'. ELA revealed localized high-error recompression, and textual claims directly contradict verified scientific consensus.",
        evidence_bullets=[
            "[DEMO RESULT] ELA showed localized compression inconsistencies around the foreground figure.",
            "[DEMO RESULT] EXIF metadata indicates processing with Adobe Photoshop 2024.",
            "[DEMO RESULT] OCR extracted sensational claims regarding moon landing staging.",
            "[DEMO RESULT] Fact verification matched historical consensus contradicting the staged moon claim.",
            "[DEMO RESULT] Experimental AI-generation baseline calculated 72.0% synthetic probability."
        ],
        score_breakdown={
            "ela": {
                "name": "Error Level Analysis",
                "score": 40.0,
                "normalized_weight_pct": 25.0,
                "confidence": "high",
                "explanation": "[DEMO RESULT] Localized difference variance detected in foreground block."
            },
            "copy_move": {
                "name": "Copy-Move Forgery",
                "score": 65.0,
                "normalized_weight_pct": 20.0,
                "confidence": "medium",
                "explanation": "[DEMO RESULT] Multiple recurring feature vectors noted across terrain background."
            },
            "ai_detector": {
                "name": "AI-Generation Estimate",
                "score": 28.0,
                "normalized_weight_pct": 20.0,
                "confidence": "medium",
                "explanation": "[DEMO RESULT] Low Laplacian variance and smooth chromatic planes."
            },
            "metadata": {
                "name": "Metadata & Provenance",
                "score": 40.0,
                "normalized_weight_pct": 10.0,
                "confidence": "high",
                "explanation": "[DEMO RESULT] Software tag: Adobe Photoshop."
            },
            "fact_check": {
                "name": "Claim Verification",
                "score": 25.0,
                "normalized_weight_pct": 15.0,
                "confidence": "high",
                "explanation": "[DEMO RESULT] Contradicted by NASA Lunar Surface Journal."
            },
            "frequency": {
                "name": "Frequency Domain (FFT)",
                "score": 60.0,
                "normalized_weight_pct": 10.0,
                "confidence": "medium",
                "explanation": "[DEMO RESULT] Moderate high-frequency attenuation."
            }
        },
        modules_results={
            "metadata": {
                "status": "success",
                "score": 40.0,
                "has_exif": True,
                "software": "Adobe Photoshop 2024",
                "camera_make": None,
                "camera_model": None,
                "explanation": "[DEMO RESULT] Header indicates manipulation in Adobe Photoshop."
            },
            "ocr": {
                "status": "success",
                "text": "BREAKING: Official statement confirmed moon landing was staged in Hollywood desert studio.",
                "confidence": 94.5,
                "bounding_boxes": []
            },
            "claims_verification": [
                {
                    "claim": "moon landing was staged in Hollywood desert studio",
                    "verdict": "CONTRADICTED",
                    "confidence": "High",
                    "evidence": "Apollo lunar landings verified by independent astronomical observatories and lunar rock samples.",
                    "source": "Smithsonian Air & Space Museum",
                    "provider": "LocalKnowledgeBase"
                }
            ]
        },
        artifacts={},
        is_demo=True
    )

    db.add(demo_record)
    db.commit()
    db.refresh(demo_record)
    return demo_record
