"""Frequency domain analysis module for VisionGuard.

Uses 2D Fast Fourier Transform (FFT) to analyze spectral energy distribution,
detecting periodic artifacts, unnatural grid spikes, and upsampling traces.
"""

from pathlib import Path
from typing import Dict, Any
import cv2
import numpy as np


def analyze_frequency_domain(
    image_path: Path,
    output_dir: Path
) -> Dict[str, Any]:
    """Computes 2D FFT magnitude spectrum and evaluates frequency distribution."""
    output_dir.mkdir(parents=True, exist_ok=True)
    vis_output_path = output_dir / "frequency.png"

    try:
        img_bgr = cv2.imread(str(image_path))
        if img_bgr is None:
            return {
                "status": "unavailable",
                "score": None,
                "confidence": "low",
                "explanation": "Image could not be read for frequency domain analysis.",
                "visualization_path": None,
                "artifact_name": None
            }

        gray = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2GRAY)
        h, w = gray.shape

        # 2D Fast Fourier Transform
        f_transform = np.fft.fft2(gray.astype(np.float32))
        f_shift = np.fft.fftshift(f_transform)
        magnitude = np.abs(f_shift)
        
        # Logarithmic scale for visualization
        log_magnitude = 20.0 * np.log(magnitude + 1.0)
        
        # Normalize to 0-255 for visualization
        norm_spectrum = cv2.normalize(log_magnitude, None, 0, 255, cv2.NORM_MINMAX)
        norm_spectrum = np.uint8(norm_spectrum)

        # Apply forensic false-color heatmap (e.g. COLORMAP_INFERNO or JET)
        heatmap = cv2.applyColorMap(norm_spectrum, cv2.COLORMAP_INFERNO)
        cv2.imwrite(str(vis_output_path), heatmap)

        # Frequency energy metrics:
        # Natural optical images follow a 1/f power law decay from DC center outwards.
        # Synthetic upsampling, GAN checkerboard patterns, or digital grid resizing show
        # distinct anomalous high-frequency spikes away from center.
        
        cy, cx = h // 2, w // 2
        radius = min(h, w) // 4
        
        # Mask center (low frequency DC components)
        y, x = np.ogrid[:h, :w]
        dist_from_center = np.sqrt((x - cx)**2 + (y - cy)**2)
        
        low_freq_mask = dist_from_center <= radius
        high_freq_mask = dist_from_center > radius

        low_freq_energy = float(np.mean(magnitude[low_freq_mask]))
        high_freq_energy = float(np.mean(magnitude[high_freq_mask]))
        
        ratio = high_freq_energy / (low_freq_energy + 1e-7)

        # Check for isolated spectral spikes in high-frequency zone
        high_freq_vals = log_magnitude[high_freq_mask]
        hf_mean = float(np.mean(high_freq_vals))
        hf_std = float(np.std(high_freq_vals))
        hf_max = float(np.max(high_freq_vals))

        spike_prominence = (hf_max - hf_mean) / (hf_std + 1e-5)

        if spike_prominence > 4.5 and ratio > 0.05:
            score = 45.0
            confidence = "medium"
            explanation = (
                f"Distinct spectral spikes detected in high-frequency spectrum (prominence: {spike_prominence:.2f}). "
                "Such periodic spikes often correlate with synthetic upsampling or GAN checkerboard artifacts. "
                "Frequency-domain analysis can indicate inconsistencies but cannot independently prove manipulation."
            )
        elif ratio < 0.0005:
            score = 65.0
            confidence = "medium"
            explanation = (
                "Unusually low high-frequency content detected (excessive smoothness or heavy compression). "
                "Frequency-domain analysis can indicate inconsistencies but cannot independently prove manipulation."
            )
        else:
            score = 88.0
            confidence = "high"
            explanation = (
                f"Harmonic frequency fall-off consistent with natural camera optics (ratio: {ratio:.4f}). "
                "No anomalous periodic grid spikes detected in the 2D Fourier spectrum. "
                "Frequency-domain analysis can indicate inconsistencies but cannot independently prove manipulation."
            )

        return {
            "status": "success",
            "score": score,
            "confidence": confidence,
            "high_low_ratio": round(ratio, 5),
            "spike_prominence": round(spike_prominence, 3),
            "visualization_path": str(vis_output_path),
            "artifact_name": "frequency.png",
            "explanation": explanation
        }

    except Exception as e:
        return {
            "status": "unavailable",
            "score": None,
            "confidence": "low",
            "explanation": f"Frequency analysis failed: {str(e)}",
            "visualization_path": None,
            "artifact_name": None
        }
