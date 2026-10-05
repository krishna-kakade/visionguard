"""Analysis Pipeline orchestrator for VisionGuard.

Executes multimodal image forensics, OCR, claim extraction, fact checking,
and decision synthesis in sequential stages with comprehensive exception isolation,
logging, and database persistence.
"""

from pathlib import Path
import logging
from typing import Dict, Any, Optional
import traceback
from sqlalchemy.orm import Session

from config import RESULTS_DIR, REPORTS_DIR
from models.database_models import AnalysisRecord
from modules.preprocessing import validate_image_file, preprocess_image
from modules.metadata_analysis import analyze_metadata
from modules.ela import perform_ela
from modules.copy_move import detect_copy_move
from modules.frequency_analysis import analyze_frequency_domain
from modules.ai_detector import AIImageDetector
from modules.ocr import extract_text
from modules.nlp import extract_claims_and_entities
from modules.fact_checker import verify_claims_list
from modules.decision_engine import evaluate_authenticity
from services.report_generator import generate_json_report, generate_pdf_report

logger = logging.getLogger("visionguard.pipeline")
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")


def update_record_status(db: Session, record_id: str, status: str, current_step: str, error_msg: Optional[str] = None):
    """Safely updates current pipeline execution stage in SQLite."""
    try:
        rec = db.query(AnalysisRecord).filter(AnalysisRecord.id == record_id).first()
        if rec:
            rec.status = status
            rec.current_step = current_step
            if error_msg:
                rec.error_message = error_msg
            db.commit()
    except Exception as e:
        logger.error(f"Failed to update record status for {record_id}: {e}")
        db.rollback()


def run_analysis_pipeline(analysis_id: str, file_path_str: str, original_filename: str, db: Session) -> Dict[str, Any]:
    """Runs end-to-end multimodal forensic verification pipeline."""
    logger.info(f"Analysis started for id: {analysis_id}, file: {original_filename}")
    image_path = Path(file_path_str)
    analysis_results_dir = RESULTS_DIR / analysis_id
    analysis_results_dir.mkdir(parents=True, exist_ok=True)
    artifacts: Dict[str, str] = {"original": str(image_path)}

    try:
        # Step 1: Image Validation
        update_record_status(db, analysis_id, "processing", "Validating image")
        logger.info(f"[{analysis_id}] Step 1: Validating image")
        is_valid, val_msg = validate_image_file(image_path)
        if not is_valid:
            logger.error(f"[{analysis_id}] Validation failed: {val_msg}")
            update_record_status(db, analysis_id, "failed", "Validation Failed", val_msg)
            return {"status": "failed", "error": val_msg}

        # Step 2: Preprocessing
        update_record_status(db, analysis_id, "processing", "Preprocessing")
        logger.info(f"[{analysis_id}] Step 2: Preprocessing")
        try:
            prep_res = preprocess_image(image_path, analysis_results_dir)
            working_image_path = Path(prep_res["preprocessed_image_path"])
            artifacts["preprocessed"] = str(working_image_path)
        except Exception as e:
            logger.warning(f"[{analysis_id}] Preprocessing error: {e}, falling back to original")
            working_image_path = image_path
            prep_res = {"status": "fallback", "explanation": f"Using original image: {str(e)}"}

        # Step 3: Metadata / EXIF Analysis
        update_record_status(db, analysis_id, "processing", "Metadata analysis")
        logger.info(f"[{analysis_id}] Step 3: Metadata analysis")
        try:
            metadata_res = analyze_metadata(image_path)
        except Exception as e:
            logger.warning(f"[{analysis_id}] Metadata analysis error: {e}")
            metadata_res = {"status": "unavailable", "score": None, "confidence": "low", "explanation": str(e), "has_exif": False}

        # Step 4: Error Level Analysis (ELA)
        update_record_status(db, analysis_id, "processing", "Error Level Analysis")
        logger.info(f"[{analysis_id}] Step 4: ELA")
        try:
            ela_res = perform_ela(working_image_path, analysis_results_dir)
            if ela_res.get("visualization_path"):
                artifacts["ela"] = ela_res["visualization_path"]
        except Exception as e:
            logger.warning(f"[{analysis_id}] ELA error: {e}")
            ela_res = {"status": "unavailable", "score": None, "confidence": "low", "explanation": str(e)}

        # Step 5: Copy-Move Forgery Detection
        update_record_status(db, analysis_id, "processing", "Copy-move detection")
        logger.info(f"[{analysis_id}] Step 5: Copy-move")
        try:
            copy_move_res = detect_copy_move(working_image_path, analysis_results_dir)
            if copy_move_res.get("visualization_path"):
                artifacts["copy_move"] = copy_move_res["visualization_path"]
        except Exception as e:
            logger.warning(f"[{analysis_id}] Copy-move error: {e}")
            copy_move_res = {"status": "unavailable", "score": None, "confidence": "low", "explanation": str(e)}

        # Step 6: Frequency Domain (FFT) Analysis
        update_record_status(db, analysis_id, "processing", "Frequency analysis")
        logger.info(f"[{analysis_id}] Step 6: Frequency analysis")
        try:
            freq_res = analyze_frequency_domain(working_image_path, analysis_results_dir)
            if freq_res.get("visualization_path"):
                artifacts["frequency"] = freq_res["visualization_path"]
        except Exception as e:
            logger.warning(f"[{analysis_id}] Frequency analysis error: {e}")
            freq_res = {"status": "unavailable", "score": None, "confidence": "low", "explanation": str(e)}

        # Step 7: AI Image Detection Baseline
        update_record_status(db, analysis_id, "processing", "AI image detection")
        logger.info(f"[{analysis_id}] Step 7: AI detection")
        try:
            ai_detector = AIImageDetector()
            ai_res = ai_detector.detect(working_image_path)
        except Exception as e:
            logger.warning(f"[{analysis_id}] AI detection error: {e}")
            ai_res = {"status": "unavailable", "ai_probability": None, "human_probability": None, "confidence": "low", "explanation": str(e), "is_experimental": True}

        # Step 8: Optical Character Recognition (OCR)
        update_record_status(db, analysis_id, "processing", "OCR extraction")
        logger.info(f"[{analysis_id}] Step 8: OCR")
        try:
            ocr_res = extract_text(image_path, analysis_results_dir)
            if ocr_res.get("visualization_path"):
                artifacts["ocr"] = ocr_res["visualization_path"]
        except Exception as e:
            logger.warning(f"[{analysis_id}] OCR error: {e}")
            ocr_res = {"status": "unavailable", "text": "", "confidence": 0.0, "bounding_boxes": [], "explanation": str(e)}

        # Step 9: NLP & Claim Extraction
        update_record_status(db, analysis_id, "processing", "NLP claim extraction")
        logger.info(f"[{analysis_id}] Step 9: NLP")
        try:
            nlp_res = extract_claims_and_entities(ocr_res.get("text", ""))
        except Exception as e:
            logger.warning(f"[{analysis_id}] NLP error: {e}")
            nlp_res = {"status": "unavailable", "entities": [], "claims": [], "explanation": str(e)}

        # Step 10: Fact Verification
        update_record_status(db, analysis_id, "processing", "Fact verification")
        logger.info(f"[{analysis_id}] Step 10: Fact verification")
        try:
            claims_verification = verify_claims_list(nlp_res.get("claims", []))
        except Exception as e:
            logger.warning(f"[{analysis_id}] Fact verification error: {e}")
            claims_verification = []

        # Step 11: Explainable Decision Engine Synthesis
        update_record_status(db, analysis_id, "processing", "Decision engine synthesis")
        logger.info(f"[{analysis_id}] Step 11: Decision engine")
        decision_res = evaluate_authenticity(
            metadata_res=metadata_res,
            ela_res=ela_res,
            copy_move_res=copy_move_res,
            freq_res=freq_res,
            ai_res=ai_res,
            ocr_res=ocr_res,
            claims_verification=claims_verification
        )

        # Aggregate complete modules payload
        modules_payload = {
            "preprocessing": prep_res,
            "metadata": metadata_res,
            "ela": ela_res,
            "copy_move": copy_move_res,
            "frequency": freq_res,
            "ai_detector": ai_res,
            "ocr": ocr_res,
            "nlp": nlp_res,
            "claims_verification": claims_verification
        }

        # Step 12: Save Reports (JSON & PDF)
        update_record_status(db, analysis_id, "processing", "Generating reports")
        logger.info(f"[{analysis_id}] Step 12: Generating reports")
        json_report_path = REPORTS_DIR / f"{analysis_id}.json"
        pdf_report_path = REPORTS_DIR / f"{analysis_id}.pdf"

        report_context = {
            "id": analysis_id,
            "filename": Path(file_path_str).name,
            "original_filename": original_filename,
            "status": "completed",
            "overall_score": decision_res.get("overall_score"),
            "authenticity_status": decision_res.get("authenticity_status"),
            "ai_probability": ai_res.get("ai_probability"),
            "confidence": decision_res.get("confidence"),
            "extracted_text": ocr_res.get("text", ""),
            "final_summary": decision_res.get("final_summary"),
            "evidence_bullets": decision_res.get("evidence_bullets", []),
            "score_breakdown": decision_res.get("score_breakdown", {}),
            "modules_results": modules_payload,
            "artifacts": artifacts,
            "limitations": decision_res.get("limitations")
        }

        try:
            generate_json_report(report_context, json_report_path)
            generate_pdf_report(report_context, pdf_report_path)
        except Exception as e:
            logger.warning(f"[{analysis_id}] Report generation error: {e}")

        # Update Database Record
        rec = db.query(AnalysisRecord).filter(AnalysisRecord.id == analysis_id).first()
        if rec:
            rec.status = "completed"
            rec.current_step = "Completed"
            rec.overall_score = decision_res.get("overall_score")
            rec.authenticity_status = decision_res.get("authenticity_status")
            rec.ai_probability = ai_res.get("ai_probability")
            rec.confidence = decision_res.get("confidence")
            rec.extracted_text = ocr_res.get("text", "")
            rec.final_summary = decision_res.get("final_summary")
            rec.evidence_bullets = decision_res.get("evidence_bullets")
            rec.score_breakdown = decision_res.get("score_breakdown")
            rec.modules_results = modules_payload
            rec.artifacts = artifacts
            db.commit()

        logger.info(f"Analysis completed successfully for id: {analysis_id}")
        return report_context

    except Exception as e:
        logger.error(f"Fatal error in analysis pipeline for {analysis_id}: {traceback.format_exc()}")
        update_record_status(db, analysis_id, "failed", "Pipeline Error", str(e))
        return {"status": "failed", "error": str(e)}
