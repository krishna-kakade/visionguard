"""Automated test suite for VisionGuard backend."""

import pytest
from pathlib import Path
from fastapi.testclient import TestClient
import numpy as np

import sys
# Ensure backend directory is in sys.path
BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from main import app
from database import SessionLocal, init_db
from modules.preprocessing import validate_image_file, preprocess_image
from modules.metadata_analysis import analyze_metadata
from modules.ela import perform_ela
from modules.copy_move import detect_copy_move
from modules.frequency_analysis import analyze_frequency_domain
from modules.ai_detector import AIImageDetector
from modules.decision_engine import evaluate_authenticity
from services.analysis_pipeline import run_analysis_pipeline

client = TestClient(app)
TEST_IMAGES_DIR = Path(__file__).resolve().parent / "test_images"
OUTPUT_DIR = BASE_DIR / "results" / "test_run"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


@pytest.fixture(scope="session", autouse=True)
def setup_db():
    init_db()


def test_health():
    """Rule 4: Verify health endpoint."""
    response = client.get("/api/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert data["service"] == "VisionGuard"


def test_image_validation():
    """Rule 6: Verify upload validation rules."""
    clean_img = TEST_IMAGES_DIR / "clean_synthetic.png"
    assert clean_img.exists()
    
    # Valid image
    is_valid, msg = validate_image_file(clean_img, "image/png")
    assert is_valid is True

    # Non-existent file
    is_valid, msg = validate_image_file(Path("non_existent_file.png"))
    assert is_valid is False

    # Invalid extension
    fake_txt = OUTPUT_DIR / "bad_ext.txt"
    fake_txt.write_text("not an image")
    is_valid, msg = validate_image_file(fake_txt)
    assert is_valid is False


def test_metadata():
    """Rule 9: Test metadata extraction."""
    clean_img = TEST_IMAGES_DIR / "clean_synthetic.png"
    res = analyze_metadata(clean_img)
    assert res["status"] in ["success", "unavailable"]
    assert "dimensions" in res
    assert "format" in res
    assert res["explanation"] is not None


def test_ela():
    """Rule 10: Real Error Level Analysis."""
    recomp_img = TEST_IMAGES_DIR / "recompressed_ela.jpg"
    res = perform_ela(recomp_img, OUTPUT_DIR)
    assert res["status"] == "success"
    assert "mean_difference" in res
    assert "max_difference" in res
    assert res["score"] is not None
    assert Path(res["visualization_path"]).exists()


def test_copy_move():
    """Rule 11: Copy-move feature analysis."""
    cm_img = TEST_IMAGES_DIR / "copy_move_forgery.png"
    res = detect_copy_move(cm_img, OUTPUT_DIR)
    assert res["status"] == "success"
    assert "match_count" in res
    assert Path(res["visualization_path"]).exists()


def test_frequency_domain():
    """Rule 12: Frequency FFT analysis."""
    clean_img = TEST_IMAGES_DIR / "clean_synthetic.png"
    res = analyze_frequency_domain(clean_img, OUTPUT_DIR)
    assert res["status"] == "success"
    assert "high_low_ratio" in res
    assert Path(res["visualization_path"]).exists()


def test_ai_detector():
    """Rule 13: Transparent AI detector baseline."""
    clean_img = TEST_IMAGES_DIR / "clean_synthetic.png"
    detector = AIImageDetector()
    res = detector.detect(clean_img)
    assert res["status"] == "success"
    assert res["is_experimental"] is True
    assert 0.0 <= res["ai_probability"] <= 1.0


def test_decision_engine():
    """Rule 17 & 18: Decision engine with dynamic normalization."""
    dummy_meta = {"status": "success", "score": 60.0, "confidence": "low", "has_exif": False}
    dummy_ela = {"status": "success", "score": 85.0, "confidence": "high", "explanation": "Uniform ELA"}
    dummy_cm = {"status": "success", "score": 90.0, "confidence": "high", "suspicious_clusters": 0}
    dummy_freq = {"status": "success", "score": 80.0, "confidence": "medium"}
    dummy_ai = {"status": "success", "ai_probability": 0.20, "confidence": "medium"}
    dummy_ocr = {"status": "unavailable", "text": ""}
    dummy_claims = []

    res = evaluate_authenticity(
        dummy_meta, dummy_ela, dummy_cm, dummy_freq, dummy_ai, dummy_ocr, dummy_claims
    )
    assert res["authenticity_status"] in ["Likely Authentic", "Potentially Suspicious", "Highly Suspicious"]
    assert 0 <= res["overall_score"] <= 100
    assert len(res["evidence_bullets"]) > 0
    assert "limitations" in res


def test_pipeline_integration():
    """Rule 7: Full pipeline execution and report generation."""
    db = SessionLocal()
    try:
        clean_img = TEST_IMAGES_DIR / "clean_synthetic.png"
        analysis_id = "test-pipeline-run-001"
        res = run_analysis_pipeline(analysis_id, str(clean_img), "clean_synthetic.png", db)
        assert res["status"] == "completed"
        assert res["overall_score"] is not None
        assert "artifacts" in res
        assert Path(res["artifacts"]["original"]).exists()
    finally:
        db.close()


def test_demo_endpoint():
    """Rule 48: Demo endpoint returns explicitly labeled DEMO RESULT."""
    response = client.post("/api/demo")
    assert response.status_code == 200
    data = response.json()
    assert data["is_demo"] is True
    assert "DEMO RESULT" in data["final_summary"]
