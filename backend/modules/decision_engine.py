"""Explainable Decision Engine for VisionGuard.

Synthesizes multimodal forensic signals, AI probability, metadata provenance,
and claim verification into an explainable authenticity assessment with
dynamically normalized scoring and transparent evidence breakdown.
"""

from typing import Dict, Any, List, Optional


LIMITATIONS_STATEMENT = (
    "VisionGuard provides AI-assisted forensic analysis. Results are probabilistic "
    "and should not be treated as definitive proof of authenticity or manipulation."
)


def evaluate_authenticity(
    metadata_res: Dict[str, Any],
    ela_res: Dict[str, Any],
    copy_move_res: Dict[str, Any],
    freq_res: Dict[str, Any],
    ai_res: Dict[str, Any],
    ocr_res: Dict[str, Any],
    claims_verification: List[Dict[str, Any]]
) -> Dict[str, Any]:
    """Dynamically aggregates forensic and verification evidence into a transparent trust score."""

    # Base nominal weights
    weights_nominal = {
        "ela": 0.25,
        "copy_move": 0.20,
        "ai_detector": 0.20,
        "frequency": 0.15,
        "metadata": 0.10,
        "fact_check": 0.10
    }

    components: Dict[str, Dict[str, Any]] = {}
    active_weights_sum = 0.0

    # 1. ELA component
    if ela_res.get("status") == "success" and ela_res.get("score") is not None:
        components["ela"] = {
            "name": "Error Level Analysis",
            "score": float(ela_res["score"]),
            "weight": weights_nominal["ela"],
            "confidence": ela_res.get("confidence", "medium"),
            "explanation": ela_res.get("explanation", "")
        }
        active_weights_sum += weights_nominal["ela"]

    # 2. Copy-Move component
    if copy_move_res.get("status") == "success" and copy_move_res.get("score") is not None:
        components["copy_move"] = {
            "name": "Copy-Move Forgery",
            "score": float(copy_move_res["score"]),
            "weight": weights_nominal["copy_move"],
            "confidence": copy_move_res.get("confidence", "medium"),
            "explanation": copy_move_res.get("explanation", "")
        }
        active_weights_sum += weights_nominal["copy_move"]

    # 3. AI Detector component (invert AI probability: high AI prob = low authenticity score)
    if ai_res.get("status") == "success" and ai_res.get("ai_probability") is not None:
        ai_prob = float(ai_res["ai_probability"])
        # Score = (1.0 - ai_prob) * 100
        ai_score = round((1.0 - ai_prob) * 100, 1)
        components["ai_detector"] = {
            "name": "AI-Generation Estimate",
            "score": ai_score,
            "weight": weights_nominal["ai_detector"],
            "confidence": ai_res.get("confidence", "low"),
            "explanation": ai_res.get("explanation", "")
        }
        active_weights_sum += weights_nominal["ai_detector"]

    # 4. Frequency component
    if freq_res.get("status") == "success" and freq_res.get("score") is not None:
        components["frequency"] = {
            "name": "Frequency Domain (FFT)",
            "score": float(freq_res["score"]),
            "weight": weights_nominal["frequency"],
            "confidence": freq_res.get("confidence", "medium"),
            "explanation": freq_res.get("explanation", "")
        }
        active_weights_sum += weights_nominal["frequency"]

    # 5. Metadata component
    if metadata_res.get("status") == "success" and metadata_res.get("score") is not None:
        components["metadata"] = {
            "name": "Metadata & Provenance",
            "score": float(metadata_res["score"]),
            "weight": weights_nominal["metadata"],
            "confidence": metadata_res.get("confidence", "low"),
            "explanation": metadata_res.get("explanation", "")
        }
        active_weights_sum += weights_nominal["metadata"]

    # 6. Fact Verification component
    if claims_verification:
        has_contradicted = any(c.get("verdict") == "CONTRADICTED" for c in claims_verification)
        has_supported = any(c.get("verdict") == "SUPPORTED" for c in claims_verification)
        
        if has_contradicted:
            fact_score = 25.0
            fact_conf = "high"
            fact_exp = "One or more textual claims extracted from the image directly contradict verified facts."
        elif has_supported:
            fact_score = 90.0
            fact_conf = "high"
            fact_exp = "Textual claims extracted from the image align with verified factual records."
        else:
            fact_score = 65.0
            fact_conf = "low"
            fact_exp = "Claims could not be independently corroborated by external verification providers."

        components["fact_check"] = {
            "name": "Claim Verification",
            "score": fact_score,
            "weight": weights_nominal["fact_check"],
            "confidence": fact_conf,
            "explanation": fact_exp
        }
        active_weights_sum += weights_nominal["fact_check"]

    # If insufficient modules succeeded
    if active_weights_sum < 0.25:
        return {
            "overall_score": None,
            "authenticity_status": "Insufficient Evidence",
            "confidence": "Low",
            "score_breakdown": {},
            "evidence_bullets": [
                "Too few forensic modules could produce reliable metrics.",
                "Unable to form a dependable authenticity assessment."
            ],
            "final_summary": "Insufficient evidence to determine image authenticity.",
            "limitations": LIMITATIONS_STATEMENT
        }

    # Dynamically normalize weights across active components
    weighted_score_total = 0.0
    breakdown: Dict[str, Any] = {}

    for key, comp in components.items():
        normalized_weight = comp["weight"] / active_weights_sum
        contribution = comp["score"] * normalized_weight
        weighted_score_total += contribution
        breakdown[key] = {
            "name": comp["name"],
            "score": round(comp["score"], 1),
            "nominal_weight_pct": round(comp["weight"] * 100, 1),
            "normalized_weight_pct": round(normalized_weight * 100, 1),
            "contribution": round(contribution, 1),
            "confidence": comp["confidence"],
            "explanation": comp["explanation"]
        }

    overall_score = round(weighted_score_total, 1)

    # Determine authenticity status
    # Categories:
    # >= 75: Likely Authentic
    # 45 - 74: Potentially Suspicious
    # < 45: Highly Suspicious
    # Or Insufficient Evidence if confidence is low across the board
    
    # Check if there is a severe red flag (e.g. copy move clusters or genuine ELA block disparity)
    severe_tampering = (
        (copy_move_res.get("suspicious_clusters", 0) >= 4) or
        (ela_res.get("block_disparity", 0) >= 3.5 and ela_res.get("max_difference", 0) > 45.0 and ela_res.get("mean_difference", 0) >= 3.0)
    )

    if severe_tampering:
        # Cap score to reflect detected physical manipulation
        overall_score = min(overall_score, 40.0)

    if overall_score >= 75.0:
        authenticity_status = "Likely Authentic"
    elif overall_score >= 45.0:
        authenticity_status = "Potentially Suspicious"
    else:
        authenticity_status = "Highly Suspicious"

    # Overall Confidence Calculation
    high_conf_count = sum(1 for c in components.values() if c["confidence"] == "high")
    if high_conf_count >= 3:
        overall_confidence = "High"
    elif high_conf_count >= 1 or len(components) >= 4:
        overall_confidence = "Medium"
    else:
        overall_confidence = "Low"

    # Synthesize evidence bullets: "Why did VisionGuard reach this result?"
    evidence_bullets: List[str] = []

    # ELA bullet
    if "ela" in components:
        if ela_res.get("score", 0) < 50:
            evidence_bullets.append("ELA showed localized compression inconsistencies characteristic of digital editing or splicing.")
        else:
            evidence_bullets.append("ELA revealed consistent compression characteristics across the image surface.")
    else:
        evidence_bullets.append("Error Level Analysis was unavailable.")

    # Metadata bullet
    if metadata_res.get("has_exif"):
        if metadata_res.get("camera_make"):
            evidence_bullets.append(f"Hardware camera provenance confirmed: {metadata_res.get('camera_make')} {metadata_res.get('camera_model')}.")
        elif metadata_res.get("software"):
            evidence_bullets.append(f"Image header contains traces of editing software: {metadata_res.get('software')}.")
        else:
            evidence_bullets.append("Partial EXIF metadata was present.")
    else:
        evidence_bullets.append("No EXIF metadata was available (commonly stripped by messaging platforms).")

    # Copy-Move bullet
    if copy_move_res.get("status") == "success":
        clusters = copy_move_res.get("suspicious_clusters", 0)
        if clusters > 0:
            evidence_bullets.append(f"Feature matching identified {clusters} duplicated feature clusters indicative of copy-move cloning.")
        else:
            evidence_bullets.append("No reliable copy-move cloning evidence was found.")
    else:
        evidence_bullets.append("Copy-move detection was inconclusive.")

    # Frequency bullet
    if freq_res.get("status") == "success":
        if freq_res.get("score", 0) < 50:
            evidence_bullets.append("Fourier frequency analysis detected anomalous periodic spectral spikes.")
        else:
            evidence_bullets.append("Fourier frequency distribution is consistent with natural camera optics.")

    # AI Detector bullet
    if ai_res.get("status") == "success" and ai_res.get("ai_probability") is not None:
        ai_p = ai_res["ai_probability"] * 100
        evidence_bullets.append(f"Experimental AI-generation baseline calculated an estimated probability of {ai_p:.1f}%.")

    # OCR / Claim bullet
    if ocr_res.get("text"):
        evidence_bullets.append(f"OCR extracted textual content ('{ocr_res['text'][:60]}...').")
        if claims_verification:
            contradicted = [c for c in claims_verification if c.get("verdict") == "CONTRADICTED"]
            supported = [c for c in claims_verification if c.get("verdict") == "SUPPORTED"]
            if contradicted:
                evidence_bullets.append(f"Fact checking contradicted extracted claims: '{contradicted[0]['claim'][:60]}...'.")
            elif supported:
                evidence_bullets.append(f"Fact checking corroborated extracted claims with verified sources.")
            else:
                evidence_bullets.append("Extracted text claims could not be verified by external providers.")
    else:
        evidence_bullets.append("No embedded text was detected in the visual frame.")

    # Final summary text
    final_summary = (
        f"VisionGuard assessed this image as '{authenticity_status}' with {overall_confidence} confidence "
        f"(Overall Trust Score: {overall_score:.0f}/100). The assessment is synthesized from "
        f"{len(components)} active forensic and verification modules with dynamically normalized weighting."
    )

    return {
        "overall_score": overall_score,
        "authenticity_status": authenticity_status,
        "confidence": overall_confidence,
        "score_breakdown": breakdown,
        "evidence_bullets": evidence_bullets,
        "final_summary": final_summary,
        "limitations": LIMITATIONS_STATEMENT
    }
