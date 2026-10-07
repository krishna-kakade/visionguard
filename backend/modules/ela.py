"""Error Level Analysis (ELA) module for VisionGuard.

Performs texture-adaptive recompression difference analysis to accurately detect localized
digital splicing, differing JPEG compression levels, and image tampering while avoiding
false alarms on organic high-frequency edges.
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
    """Calculates texture-adaptive Error Level Analysis against controlled JPEG recompression."""
    output_dir.mkdir(parents=True, exist_ok=True)
    temp_jpeg_path = output_dir / "_temp_recompressed.jpg"
    ela_output_path = output_dir / "ela.png"

    try:
        # 1. Open original image
        with Image.open(image_path) as orig_img:
            orig_rgb = orig_img.convert("RGB")
            orig_np = np.array(orig_rgb, dtype=np.float32)

            # 2. Save temporary controlled JPEG at quality
            orig_rgb.save(temp_jpeg_path, "JPEG", quality=quality)

            # 3. Open recompressed image
            with Image.open(temp_jpeg_path) as recompressed_img:
                # 4. Calculate absolute pixel difference
                diff = ImageChops.difference(orig_rgb, recompressed_img)
                diff_np = np.array(diff, dtype=np.float32)

                mean_diff = float(np.mean(diff_np))
                max_diff = float(np.max(diff_np))
                std_diff = float(np.std(diff_np))

                # 5. Generate scaled ELA visualization for investigator inspection
                extrema = diff.getextrema()
                max_val = max([ex[1] for ex in extrema]) if extrema else 1
                if max_val == 0:
                    max_val = 1
                enhancer = ImageEnhance.Brightness(diff)
                enhanced_ela = enhancer.enhance(255.0 / max_val)
                enhanced_ela.save(ela_output_path, "PNG")

        # Cleanup temp file
        if temp_jpeg_path.exists():
            temp_jpeg_path.unlink()

        # -------------------------------------------------------------
        # Texture-Adaptive Block Error Analysis (16x16 tiles)
        # Prevents false alarms on crisp uncompressed graphics or dark backgrounds
        # while precisely detecting composite splices.
        # -------------------------------------------------------------
        h, w = diff_np.shape[:2]
        tile_size = 16
        num_th = h // tile_size
        num_tw = w // tile_size

        tile_errors = []
        tile_textures = []

        if num_th >= 2 and num_tw >= 2:
            # Convert to luminance diff
            lum_diff = 0.299 * diff_np[:, :, 0] + 0.587 * diff_np[:, :, 1] + 0.114 * diff_np[:, :, 2]
            lum_orig = 0.299 * orig_np[:, :, 0] + 0.587 * orig_np[:, :, 1] + 0.114 * orig_np[:, :, 2]

            for ty in range(num_th):
                for tx in range(num_tw):
                    sub_d = lum_diff[ty*tile_size:(ty+1)*tile_size, tx*tile_size:(tx+1)*tile_size]
                    sub_o = lum_orig[ty*tile_size:(ty+1)*tile_size, tx*tile_size:(tx+1)*tile_size]
                    tile_errors.append(float(np.mean(sub_d)))
                    tile_textures.append(float(np.std(sub_o)))

            tile_errors = np.array(tile_errors, dtype=np.float32)
            tile_textures = np.array(tile_textures, dtype=np.float32)

            # Normalized error relative to local tile texture
            # Natural high texture creates higher ELA, so texture-normalized error = error / (texture + 5.0)
            norm_tile_errors = tile_errors / (tile_textures + 5.0)

            p95_err = float(np.percentile(norm_tile_errors, 95))
            p50_err = float(np.percentile(norm_tile_errors, 50))
            block_disparity = p95_err / (p50_err + 1e-4)
        else:
            block_disparity = 1.0

        # Anomaly ratio
        anomaly_ratio = std_diff / (mean_diff + 1e-5)

        # -------------------------------------------------------------
        # Scientific Decision Logic
        # 1. If global mean difference is tiny (< 3.0), the image has negligible recompression error
        #    and is uniformly consistent across its canvas!
        # 2. If mean difference is significant AND block disparity is elevated, a foreign block
        #    exhibits discordant compression history (Splicing).
        # -------------------------------------------------------------
        if mean_diff < 3.0 and block_disparity < 2.5:
            # Clean uniform compression
            score = 92.0
            confidence = "high"
            explanation = (
                f"Uniform error level distribution across all image blocks (mean: {mean_diff:.2f}, std: {std_diff:.2f}). "
                "Low overall recompression error confirms consistent compression history without localized digital splicing."
            )
        elif block_disparity >= 3.5 and max_diff > 45.0 and mean_diff >= 3.0:
            # Strong localized anomaly
            score = 30.0
            confidence = "high"
            explanation = (
                f"Texture-adaptive ELA detected significant localized recompression disparity (block disparity: {block_disparity:.2f}, max error: {max_diff:.1f}). "
                "Specific image tiles deviate sharply from the ambient compression baseline, indicating foreign composite elements or localized splicing."
            )
        elif block_disparity >= 2.4 and max_diff > 35.0:
            # Moderate variation
            score = 58.0
            confidence = "medium"
            explanation = (
                f"Moderate variation in error levels detected across image blocks (block disparity: {block_disparity:.2f}, std: {std_diff:.2f}). "
                "Certain regions display minor compression discrepancies that warrant visual inspection in the artifact viewer."
            )
        else:
            score = 85.0
            confidence = "high"
            explanation = (
                f"Consistent error level characteristics across image features (mean: {mean_diff:.2f}, block disparity: {block_disparity:.2f}). "
                "No localized compression discrepancies or composite splicing seams were detected."
            )

        return {
            "status": "success",
            "score": score,
            "confidence": confidence,
            "mean_difference": round(mean_diff, 3),
            "max_difference": round(max_diff, 3),
            "std_difference": round(std_diff, 3),
            "anomaly_ratio": round(anomaly_ratio, 3),
            "block_disparity": round(block_disparity, 3),
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
