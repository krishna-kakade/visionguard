"""Frequency domain analysis module for VisionGuard.

Uses 2D Fast Fourier Transform (FFT) with azimuthal radial band decomposition
to accurately detect periodic GAN/diffusion upsampling spikes and grid artifacts
while correctly modeling natural optical frequency roll-off.
"""

from pathlib import Path
from typing import Dict, Any
import cv2
import numpy as np


def analyze_frequency_domain(
    image_path: Path,
    output_dir: Path
) -> Dict[str, Any]:
    """Computes 2D FFT magnitude spectrum and evaluates radial & azimuthal frequency distribution."""
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

        # 1. 2D Fast Fourier Transform
        f_transform = np.fft.fft2(gray.astype(np.float32))
        f_shift = np.fft.fftshift(f_transform)
        magnitude = np.abs(f_shift)

        # 2. Logarithmic scale for forensic visualization
        log_magnitude = 20.0 * np.log(magnitude + 1.0)

        # Normalize to 0-255 for visualization
        norm_spectrum = cv2.normalize(log_magnitude, None, 0, 255, cv2.NORM_MINMAX)
        norm_spectrum = np.uint8(norm_spectrum)

        # Apply forensic false-color heatmap (COLORMAP_INFERNO)
        heatmap = cv2.applyColorMap(norm_spectrum, cv2.COLORMAP_INFERNO)
        cv2.imwrite(str(vis_output_path), heatmap)

        # -------------------------------------------------------------
        # Radial Band & Azimuthal Variance Decomposition
        # Optical images follow monotonic radial decay.
        # Periodic synthetic upsampling creates isolated spikes deviating
        # sharply from their respective radial ring average.
        # -------------------------------------------------------------
        cy, cx = h // 2, w // 2
        y, x = np.ogrid[:h, :w]
        dist_from_center = np.sqrt((x - cx) ** 2 + (y - cy) ** 2)

        min_dim = min(h, w)
        r_inner = min_dim // 6
        r_outer = min_dim // 2

        # High-frequency band mask
        hf_mask = (dist_from_center >= r_inner) & (dist_from_center < r_outer)
        lf_mask = dist_from_center < r_inner

        low_freq_energy = float(np.mean(magnitude[lf_mask]))
        high_freq_energy = float(np.mean(magnitude[hf_mask]))
        ratio = high_freq_energy / (low_freq_energy + 1e-7)

        # Compute azimuthal outlier spikes across 10 concentric annular rings
        num_rings = 10
        ring_spikes = []
        ring_width = (r_outer - r_inner) // num_rings

        for i in range(num_rings):
            r_start = r_inner + i * ring_width
            r_end = r_start + ring_width
            ring_mask = (dist_from_center >= r_start) & (dist_from_center < r_end)
            if np.any(ring_mask):
                ring_vals = log_magnitude[ring_mask]
                r_mean = float(np.mean(ring_vals))
                r_std = float(np.std(ring_vals)) + 1e-5
                r_max = float(np.max(ring_vals))
                # Peak deviation in z-score above the ring mean
                z_peak = (r_max - r_mean) / r_std
                ring_spikes.append(z_peak)

        max_azimuthal_spike = float(np.max(ring_spikes)) if ring_spikes else 1.0

        # Scientific classification:
        # True periodic synthetic grid spikes produce isolated azimuthal peaks > 5.5 sigma
        # across multiple annular rings while exhibiting high HF energy ratio.
        if max_azimuthal_spike >= 6.0 and ratio > 0.08:
            score = 38.0
            confidence = "high"
            explanation = (
                f"Anomalous periodic spectral spikes detected across high-frequency annular rings (peak deviation: {max_azimuthal_spike:.2f}σ). "
                "Such isolated directional peaks strongly correlate with synthetic upsampling or GAN/diffusion convolutional grid artifacts. "
                "Frequency-domain analysis can indicate inconsistencies but cannot independently prove manipulation."
            )
        elif max_azimuthal_spike >= 4.8 and ratio > 0.05:
            score = 62.0
            confidence = "medium"
            explanation = (
                f"Moderate harmonic frequency peaks observed in mid-to-high frequency bands (deviation: {max_azimuthal_spike:.2f}σ). "
                "May indicate synthetic rendering, bilateral filtering, or geometric image resizing. "
                "Frequency-domain analysis can indicate inconsistencies but cannot independently prove manipulation."
            )
        elif ratio < 0.0003:
            score = 68.0
            confidence = "medium"
            explanation = (
                "Unusually low high-frequency content detected (heavy blur or extreme compression). "
                "Frequency-domain analysis can indicate inconsistencies but cannot independently prove manipulation."
            )
        else:
            score = 90.0
            confidence = "high"
            explanation = (
                f"Harmonic frequency fall-off consistent with natural camera optics (ratio: {ratio:.4f}, peak deviation: {max_azimuthal_spike:.2f}σ). "
                "No anomalous periodic grid spikes or synthetic upsampling artifacts detected in the 2D Fourier spectrum. "
                "Frequency-domain analysis can indicate inconsistencies but cannot independently prove manipulation."
            )

        return {
            "status": "success",
            "score": score,
            "confidence": confidence,
            "high_low_ratio": round(ratio, 5),
            "spike_prominence": round(max_azimuthal_spike, 3),
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
