"""AI-Generated Image Detector module for VisionGuard.

Implements an explainable forensic baseline analyzing chromatic entropy,
Laplacian noise variance, and gradient smoothness to estimate AI generation probability.
"""

from pathlib import Path
from typing import Dict, Any
import cv2
import numpy as np


class AIImageDetector:
    """Forensic baseline detector for identifying synthetic / AI-generated image characteristics."""

    def __init__(self, model_name: str = "visionguard-forensic-baseline-v1"):
        self.model_name = model_name

    def detect(self, image_path: Path) -> Dict[str, Any]:
        """Calculates dynamic AI generation probability based on structural and noise metrics."""
        try:
            img = cv2.imread(str(image_path))
            if img is None:
                return {
                    "status": "unavailable",
                    "ai_probability": None,
                    "human_probability": None,
                    "confidence": "low",
                    "model_name": self.model_name,
                    "is_experimental": True,
                    "explanation": "Image file could not be decoded for AI detection."
                }

            # 1. High-frequency noise residual via Laplacian variance
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            laplacian = cv2.Laplacian(gray, cv2.CV_64F)
            lap_var = float(np.var(laplacian))

            # 2. Chromatic covariance & color saturation distribution
            # Diffusion and GAN generators frequently exhibit ultra-smooth chroma planes compared to noisy camera sensors
            hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
            s_channel = hsv[:, :, 1]
            s_std = float(np.std(s_channel))
            s_mean = float(np.mean(s_channel))

            # 3. High-gradient edge transitions (smoothness vs natural sensor noise)
            sobelx = cv2.Sobel(gray, cv2.CV_64F, 1, 0, ksize=3)
            sobely = cv2.Sobel(gray, cv2.CV_64F, 0, 1, ksize=3)
            grad_mag = np.sqrt(sobelx**2 + sobely**2)
            grad_mean = float(np.mean(grad_mag))
            grad_std = float(np.std(grad_mag))

            # 4. Color channel correlation (R vs B channel residuals)
            b, g, r = cv2.split(img.astype(np.float32))
            diff_rg = np.abs(r - g)
            diff_gb = np.abs(g - b)
            color_disparity = float(np.mean(diff_rg) + np.mean(diff_gb))

            # Mathematical feature aggregation:
            # - Extreme smoothness in Laplacian (var < 80) is typical in synthetic faces / smooth renders
            # - Synthetic images often exhibit high color saturation mean with low texture entropy
            synthetic_score = 0.0

            # Laplacian factor (smoothness penalty)
            if lap_var < 100:
                synthetic_score += 0.35 * (1.0 - (lap_var / 100.0))
            elif lap_var > 600:
                # Very textured or noisy (likely natural or heavy grain)
                synthetic_score -= 0.15

            # Gradient distribution factor
            grad_ratio = grad_std / (grad_mean + 1e-5)
            if grad_ratio > 2.0:
                # Natural high dynamic range edges
                synthetic_score -= 0.10
            elif grad_ratio < 1.3:
                # Artificial uniform sharpness/blur
                synthetic_score += 0.20

            # Saturation / Chroma smoothness
            if s_mean > 110 and s_std < 40:
                synthetic_score += 0.25

            # Bound AI probability dynamically between [0.08, 0.92]
            base_prob = 0.35 + synthetic_score
            ai_prob = float(np.clip(base_prob, 0.08, 0.92))
            human_prob = float(np.clip(1.0 - ai_prob, 0.08, 0.92))

            # Confidence determination
            if ai_prob >= 0.70 or ai_prob <= 0.25:
                confidence = "medium"
            else:
                confidence = "low"

            if ai_prob > 0.65:
                explanation = (
                    f"Experimental AI-generation estimate is elevated ({ai_prob*100:.1f}%). "
                    f"Observed low high-frequency sensor noise (Laplacian variance: {lap_var:.1f}) "
                    "and synthetic edge characteristics common in diffusion/generative pipelines."
                )
            elif ai_prob < 0.35:
                explanation = (
                    f"Experimental AI-generation estimate is low ({ai_prob*100:.1f}%). "
                    f"Image exhibits natural optical grain and sensor variance (Laplacian variance: {lap_var:.1f}), "
                    "characteristic of organic camera photography."
                )
            else:
                explanation = (
                    f"Experimental AI-generation estimate is indeterminate ({ai_prob*100:.1f}%). "
                    "Textural and chromatic metrics fall in an ambiguous boundary between natural rendering and generation."
                )

            return {
                "status": "success",
                "ai_probability": round(ai_prob, 3),
                "human_probability": round(human_prob, 3),
                "confidence": confidence,
                "model_name": self.model_name,
                "is_experimental": True,
                "metrics": {
                    "laplacian_variance": round(lap_var, 2),
                    "saturation_mean": round(s_mean, 2),
                    "gradient_ratio": round(grad_ratio, 3),
                    "color_disparity": round(color_disparity, 2)
                },
                "explanation": explanation
            }

        except Exception as e:
            return {
                "status": "unavailable",
                "ai_probability": None,
                "human_probability": None,
                "confidence": "low",
                "model_name": self.model_name,
                "is_experimental": True,
                "explanation": f"AI detector calculation failed: {str(e)}"
            }
