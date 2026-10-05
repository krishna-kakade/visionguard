"""Image preprocessing module for VisionGuard.

Handles image validation, loading, normalization, aspect-ratio preserving resizing,
and noise reduction without mutating or overwriting the original input.
"""

import os
from pathlib import Path
from typing import Tuple, Dict, Any, Optional
import cv2
import numpy as np
from PIL import Image, ImageOps

from config import MAX_UPLOAD_SIZE_BYTES, ALLOWED_EXTENSIONS, ALLOWED_MIME_TYPES


def validate_image_file(file_path: Path, mime_type: Optional[str] = None) -> Tuple[bool, str]:
    """Validates file existence, size, extension, and integrity."""
    if not file_path.exists():
        return False, "File does not exist on disk."

    file_size = file_path.stat().st_size
    if file_size == 0:
        return False, "Uploaded file is empty (0 bytes)."
    if file_size > MAX_UPLOAD_SIZE_BYTES:
        return False, f"File size exceeds maximum allowed limit of {MAX_UPLOAD_SIZE_BYTES // (1024*1024)}MB."

    ext = file_path.suffix.lower()
    if ext not in ALLOWED_EXTENSIONS:
        return False, f"File extension '{ext}' is not supported. Allowed: {', '.join(sorted(ALLOWED_EXTENSIONS))}"

    if mime_type and mime_type.lower() not in ALLOWED_MIME_TYPES:
        return False, f"MIME type '{mime_type}' is not an authorized image format."

    try:
        with Image.open(file_path) as img:
            img.verify()
    except Exception as e:
        return False, f"Image file is corrupted or unreadable: {str(e)}"

    return True, "Valid image"


def load_image(file_path: Path) -> Tuple[np.ndarray, Image.Image]:
    """Safely loads an image as both OpenCV BGR array and PIL Image.
    Handles EXIF orientation so image coordinates are aligned.
    """
    pil_img = Image.open(file_path)
    try:
        pil_img = ImageOps.exif_transpose(pil_img)
    except Exception:
        pass

    if pil_img.mode != "RGB":
        pil_img = pil_img.convert("RGB")

    cv_img = cv2.cvtColor(np.array(pil_img), cv2.COLOR_RGB2BGR)
    return cv_img, pil_img


def resize_image(image: np.ndarray, max_dimension: int = 1600) -> Tuple[np.ndarray, float]:
    """Resizes image if its dimensions exceed max_dimension, preserving aspect ratio."""
    h, w = image.shape[:2]
    if max(h, w) <= max_dimension:
        return image.copy(), 1.0

    scale = max_dimension / float(max(h, w))
    new_w = int(w * scale)
    new_h = int(h * scale)
    resized = cv2.resize(image, (new_w, new_h), interpolation=cv2.INTER_AREA)
    return resized, scale


def normalize_image(image: np.ndarray) -> np.ndarray:
    """Normalizes image color channels to standard contrast range."""
    lab = cv2.cvtColor(image, cv2.COLOR_BGR2LAB)
    l, a, b = cv2.split(lab)
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
    cl = clahe.apply(l)
    limg = cv2.merge((cl, a, b))
    return cv2.cvtColor(limg, cv2.COLOR_LAB2BGR)


def reduce_noise(image: np.ndarray) -> np.ndarray:
    """Applies gentle edge-preserving bilateral filtering to reduce sensor noise."""
    return cv2.bilateralFilter(image, d=5, sigmaColor=50, sigmaSpace=50)


def preprocess_image(input_path: Path, output_dir: Path) -> Dict[str, Any]:
    """Runs full preprocessing pipeline and saves normalized working image."""
    output_dir.mkdir(parents=True, exist_ok=True)
    cv_img, pil_img = load_image(input_path)
    orig_h, orig_w = cv_img.shape[:2]

    working_img, scale = resize_image(cv_img, max_dimension=1600)
    proc_h, proc_w = working_img.shape[:2]
    
    preprocessed_path = output_dir / "preprocessed.png"
    cv2.imwrite(str(preprocessed_path), working_img)

    return {
        "status": "success",
        "original_dimensions": {"width": orig_w, "height": orig_h},
        "processed_dimensions": {"width": proc_w, "height": proc_h},
        "scale_factor": scale,
        "preprocessed_image_path": str(preprocessed_path),
        "explanation": f"Image loaded successfully ({orig_w}x{orig_h}). Scaled to {proc_w}x{proc_h} for consistent forensic analysis."
    }
