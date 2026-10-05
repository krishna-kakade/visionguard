"""Optical Character Recognition (OCR) module for VisionGuard.

Safely attempts Tesseract / EasyOCR with graceful fallback to 'unavailable' status
if OCR engines are not locally installed on the host system.
"""

from pathlib import Path
from typing import Dict, Any, List
import cv2
import numpy as np
from PIL import Image

try:
    import pytesseract
except ImportError:
    pytesseract = None

try:
    import easyocr
except ImportError:
    easyocr = None


def extract_text(image_path: Path, output_dir: Path) -> Dict[str, Any]:
    """Attempts to extract text, confidence scores, and bounding boxes from the image."""
    output_dir.mkdir(parents=True, exist_ok=True)
    annotated_output_path = output_dir / "ocr_annotated.png"

    # Attempt 1: Tesseract OCR
    if pytesseract is not None:
        try:
            with Image.open(image_path) as pil_img:
                data = pytesseract.image_to_data(pil_img, output_type=pytesseract.Output.DICT)
                
                extracted_words = []
                confidences = []
                boxes = []
                
                n_boxes = len(data["text"])
                cv_img = cv2.imread(str(image_path))
                
                for i in range(n_boxes):
                    text = data["text"][i].strip()
                    conf = float(data["conf"][i])
                    if conf > 20 and text:
                        extracted_words.append(text)
                        confidences.append(conf)
                        x, y, w, h = data["left"][i], data["top"][i], data["width"][i], data["height"][i]
                        boxes.append({"text": text, "x": x, "y": y, "width": w, "height": h, "confidence": conf})
                        
                        if cv_img is not None:
                            cv2.rectangle(cv_img, (x, y), (x + w, y + h), (0, 220, 0), 2)
                            cv2.putText(
                                cv_img, text, (x, max(15, y - 5)),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 220, 0), 1, cv2.LINE_AA
                            )

                full_text = " ".join(extracted_words).strip()
                avg_conf = float(np.mean(confidences)) if confidences else 0.0

                if cv_img is not None:
                    cv2.imwrite(str(annotated_output_path), cv_img)

                return {
                    "status": "success",
                    "engine": "pytesseract",
                    "text": full_text,
                    "confidence": round(avg_conf, 1),
                    "bounding_boxes": boxes,
                    "boxes_count": len(boxes),
                    "visualization_path": str(annotated_output_path) if boxes else None,
                    "artifact_name": "ocr_annotated.png" if boxes else None,
                    "explanation": f"Extracted {len(extracted_words)} words with average confidence {avg_conf:.1f}% using Tesseract."
                }
        except Exception:
            # Tesseract binary not installed on machine or failed
            pass

    # Attempt 2: EasyOCR
    if easyocr is not None:
        try:
            reader = easyocr.Reader(['en'], gpu=False)
            results = reader.readtext(str(image_path))
            
            extracted_words = []
            confidences = []
            boxes = []
            cv_img = cv2.imread(str(image_path))

            for bbox, text, conf in results:
                if text.strip():
                    extracted_words.append(text.strip())
                    confidences.append(conf * 100)
                    
                    pts = np.array(bbox, np.int32).reshape((-1, 1, 2))
                    if cv_img is not None:
                        cv2.polylines(cv_img, [pts], isClosed=True, color=(0, 220, 0), thickness=2)
                    
                    x_min = int(min(p[0] for p in bbox))
                    y_min = int(min(p[1] for p in bbox))
                    x_max = int(max(p[0] for p in bbox))
                    y_max = int(max(p[1] for p in bbox))
                    
                    boxes.append({
                        "text": text.strip(),
                        "x": x_min,
                        "y": y_min,
                        "width": x_max - x_min,
                        "height": y_max - y_min,
                        "confidence": round(conf * 100, 1)
                    })

            full_text = " ".join(extracted_words).strip()
            avg_conf = float(np.mean(confidences)) if confidences else 0.0

            if cv_img is not None:
                cv2.imwrite(str(annotated_output_path), cv_img)

            return {
                "status": "success",
                "engine": "easyocr",
                "text": full_text,
                "confidence": round(avg_conf, 1),
                "bounding_boxes": boxes,
                "boxes_count": len(boxes),
                "visualization_path": str(annotated_output_path) if boxes else None,
                "artifact_name": "ocr_annotated.png" if boxes else None,
                "explanation": f"Extracted {len(extracted_words)} text blocks with confidence {avg_conf:.1f}% using EasyOCR."
            }
        except Exception:
            pass

    # Graceful degradation per Rule 14 & Rule 44
    return {
        "status": "unavailable",
        "engine": "none",
        "text": "",
        "confidence": 0.0,
        "bounding_boxes": [],
        "boxes_count": 0,
        "visualization_path": None,
        "artifact_name": None,
        "explanation": "OCR engine (Tesseract or EasyOCR) is not installed or configured on the host system."
    }
