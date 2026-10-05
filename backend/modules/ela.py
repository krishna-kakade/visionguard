"""Error Level Analysis (ELA) module for VisionGuard.

Performs recompression difference analysis to detect localized digital splicing,
differing JPEG compression levels, and image tampering.
"""

from pathlib import Path
from typing import Dict, Any
import numpy as np
from PIL import Image, ImageChops, ImageEnhance


def perform_ela(
    image_path: Path,
    output_dir: Path,
    quality: int = 90,
    scale_multiplier: float = 15.0
) -> Dict[str, Any]:
    """Calculates Error Level Analysis against a controlled JPEG recompression."""
    output_dir.mkdir(parents=True, exist_ok=True)
    temp_jpeg_path = output_dir / "_temp_recompressed.jpg"
    ela_output_path = output_dir / "ela.png"

    try:
        # 1. Open original image
        with Image.open(image_path) as orig_img:
            orig_rgb = orig_img.convert("RGB")
            
            # 2. Save temporary controlled JPEG
            orig_rgb.save(temp_jpeg_path, "JPEG", quality=quality)

            # 3. Open recompressed image
            with Image.open(temp_jpeg_path) as recompressed_img:
                # 4. Calculate absolute pixel difference
                diff = ImageChops.difference(orig_rgb, recompressed_img)
                
                # 5. Extract statistics from differences
                diff_np = np.array(diff, dtype=np.float32)
                mean_diff = float(np.mean(diff_np))
                max_diff = float(np.max(diff_np))
                std_diff = float(np.std(diff_np))

                # 6. Scale differences for human forensic visualization
                # If maximum difference is tiny, enhance visibility proportionally
                if max_diff > 0:
                    scale = 255.0 / max_diff if max_diff < 20 else scale_multiplier
                else:
                    scale = scale_multiplier

                extrema = diff.getextrema()
                max_val = max([ex[1] for ex in extrema])
                if max_val == 0:
                    max_val = 1
                enhancer = ImageEnhance.Brightness(diff)
                enhanced_ela = enhancer.enhance(255.0 / max_val)

                # Save ELA visualization
                enhanced_ela.save(ela_output_path, "PNG")

        # Cleanup temp file
        if temp_jpeg_path.exists():
            temp_jpeg_path.unlink()

        # Scientific evaluation of ELA statistics:
        # Standard unedited JPEGs have uniform, distributed recompression noise (low std_diff relative to mean).
        # Spliced regions introduced from different sources show localized intense bright error patterns (high std / high max_diff).
        
        # Calculate consistency score (0 to 100):
        # High score = uniform error distribution (likely consistent single-source compression)
        # Low score = high localized anomaly disparity (suspicious recompression inconsistency)
        
        anomaly_ratio = std_diff / (mean_diff + 1e-5)
        
        if anomaly_ratio > 2.2 and max_diff > 45:
            score = 35.0
            confidence = "high"
            explanation = (
                f"ELA identified regions with unusual recompression differences (std: {std_diff:.2f}, max: {max_diff:.1f}). "
                "Localized high-contrast error levels indicate that sections of this image may have different compression histories or were digitally spliced."
            )
        elif anomaly_ratio > 1.6 and max_diff > 30:
            score = 60.0
            confidence = "medium"
            explanation = (
                f"Moderate variation in error levels detected across image blocks (std: {std_diff:.2f}). "
                "Some regions display minor compression discrepancies that warrant inspection."
            )
        else:
            score = 88.0
            confidence = "high"
            explanation = (
                f"Uniform error level distribution observed across the image (mean: {mean_diff:.2f}, std: {std_diff:.2f}). "
                "No localized compression discrepancies or obvious splicing edges were detected."
            )

        return {
            "status": "success",
            "score": score,
            "confidence": confidence,
            "mean_difference": round(mean_diff, 3),
            "max_difference": round(max_diff, 3),
            "std_difference": round(std_diff, 3),
            "anomaly_ratio": round(anomaly_ratio, 3),
            "visualization_path": str(ela_output_path),
            "artifact_name": "ela.png",
            "explanation": explanation
        }

    except Exception as e:
        if temp_jpeg_path.exists():
            temp_jpeg_path.unlink()
        return {
            "status": "unavailable",
            "score": None,
            "confidence": "low",
            "explanation": f"Error Level Analysis could not be computed: {str(e)}",
            "visualization_path": None,
            "artifact_name": None
        }
