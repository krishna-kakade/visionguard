"""Copy-Move Forgery Detection module for VisionGuard.

Uses keypoint feature matching (SIFT/ORB) with Lowe's ratio test, spatial distance
constraints, and translation displacement vector clustering to identify cloned regions.
"""

from pathlib import Path
from typing import Dict, Any, List, Tuple
import cv2
import numpy as np


def detect_copy_move(
    image_path: Path,
    output_dir: Path,
    min_spatial_distance: float = 35.0,
    max_features: int = 2000
) -> Dict[str, Any]:
    """Detects duplicated / cloned image regions using feature keypoint self-matching."""
    output_dir.mkdir(parents=True, exist_ok=True)
    vis_output_path = output_dir / "copy_move.png"

    try:
        img_bgr = cv2.imread(str(image_path))
        if img_bgr is None:
            return {
                "status": "unavailable",
                "score": None,
                "confidence": "low",
                "explanation": "Image file could not be decoded by OpenCV for copy-move analysis.",
                "visualization_path": None,
                "artifact_name": None
            }

        gray = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2GRAY)

        # Prefer SIFT if available, otherwise ORB
        detector = None
        matcher = None
        is_sift = False

        try:
            detector = cv2.SIFT_create(nfeatures=max_features, contrastThreshold=0.03)
            matcher = cv2.BFMatcher(cv2.NORM_L2)
            is_sift = True
        except Exception:
            detector = cv2.ORB_create(nfeatures=max_features)
            matcher = cv2.BFMatcher(cv2.NORM_HAMMING)

        keypoints, descriptors = detector.detectAndCompute(gray, None)

        if descriptors is None or len(keypoints) < 15:
            cv2.imwrite(str(vis_output_path), img_bgr)
            return {
                "status": "success",
                "score": 85.0,
                "confidence": "low",
                "match_count": 0,
                "suspicious_clusters": 0,
                "explanation": "Insufficient feature keypoints detected for copy-move analysis (e.g. flat color or low texture).",
                "visualization_path": str(vis_output_path),
                "artifact_name": "copy_move.png"
            }

        # Find 3 nearest neighbors for each descriptor
        # match_group[0] is self (dist = 0)
        # match_group[1] is 1st closest other
        # match_group[2] is 2nd closest other
        knn_matches = matcher.knnMatch(descriptors, descriptors, k=min(4, len(descriptors)))

        valid_pairs: List[Tuple[cv2.KeyPoint, cv2.KeyPoint, np.ndarray]] = []
        vectors: List[Tuple[float, float]] = []

        ratio_thresh = 0.72 if is_sift else 0.75

        for match_group in knn_matches:
            if len(match_group) < 3:
                continue

            # Identify distinct neighbors excluding self
            other_matches = [m for m in match_group if m.queryIdx != m.trainIdx]
            if len(other_matches) < 2:
                continue

            m1 = other_matches[0]
            m2 = other_matches[1]

            # Lowe's ratio test on the two distinct closest neighbors
            if m1.distance >= ratio_thresh * m2.distance:
                continue

            kp1 = keypoints[m1.queryIdx]
            kp2 = keypoints[m1.trainIdx]

            pt1 = np.array(kp1.pt, dtype=np.float32)
            pt2 = np.array(kp2.pt, dtype=np.float32)
            spatial_dist = float(np.linalg.norm(pt1 - pt2))

            # Must be distinct locations across canvas (not adjacent pixel noise)
            if spatial_dist > min_spatial_distance:
                disp_vector = pt2 - pt1
                valid_pairs.append((kp1, kp2, disp_vector))
                vectors.append((float(disp_vector[0]), float(disp_vector[1])))

        # -------------------------------------------------------------
        # Directional Displacement Vector Clustering
        # Genuine copy-move forgeries possess multiple keypoint pairs
        # sharing identical spatial translation vector (angle and length).
        # -------------------------------------------------------------
        clustered_count = 0
        clustered_pairs = []

        if len(vectors) >= 3:
            vec_arr = np.array(vectors, dtype=np.float32)
            angles = np.arctan2(vec_arr[:, 1], vec_arr[:, 0])
            mags = np.linalg.norm(vec_arr, axis=1)

            for i in range(len(vectors)):
                consistent_matches = 0
                for j in range(len(vectors)):
                    if i != j:
                        # Angle diff in circular space
                        angle_diff = np.abs(np.arctan2(np.sin(angles[i] - angles[j]), np.cos(angles[i] - angles[j])))
                        mag_diff = abs(mags[i] - mags[j]) / (max(mags[i], mags[j]) + 1e-5)
                        if angle_diff < 0.12 and mag_diff < 0.15:
                            consistent_matches += 1

                # At least 3 other vectors must share the exact parallel translation
                if consistent_matches >= 3:
                    clustered_count += 1
                    clustered_pairs.append(valid_pairs[i])

        # Visualization output
        vis_img = img_bgr.copy()

        # Draw candidate lines in muted slate/blue, genuine clustered clones in distinct orange/crimson
        for kp1, kp2, _ in valid_pairs[:35]:
            p1 = (int(kp1.pt[0]), int(kp1.pt[1]))
            p2 = (int(kp2.pt[0]), int(kp2.pt[1]))
            cv2.line(vis_img, p1, p2, (180, 140, 60), 1, cv2.LINE_AA)
            cv2.circle(vis_img, p1, 3, (200, 160, 80), -1)
            cv2.circle(vis_img, p2, 3, (200, 160, 80), -1)

        for kp1, kp2, _ in clustered_pairs:
            p1 = (int(kp1.pt[0]), int(kp1.pt[1]))
            p2 = (int(kp2.pt[0]), int(kp2.pt[1]))
            cv2.line(vis_img, p1, p2, (30, 60, 225), 2, cv2.LINE_AA)
            cv2.circle(vis_img, p1, 5, (20, 40, 230), -1)
            cv2.circle(vis_img, p2, 5, (20, 40, 230), -1)

        cv2.imwrite(str(vis_output_path), vis_img)

        # Evaluate score
        if clustered_count >= 6:
            score = 25.0
            confidence = "high"
            explanation = (
                f"Suspicious cloned structures confirmed: {clustered_count} feature pairs share identical translation displacement vectors. "
                "Strong indication of copy-move cloning or duplicated visual objects."
            )
        elif clustered_count >= 3:
            score = 52.0
            confidence = "medium"
            explanation = (
                f"Possible duplicated regions detected: {clustered_count} feature pairs exhibit aligned spatial displacement. "
                "May indicate cloning or natural repetitive scene symmetry."
            )
        elif len(valid_pairs) > 18:
            score = 72.0
            confidence = "medium"
            explanation = (
                f"Detected {len(valid_pairs)} scattered keypoint matches across the image. "
                "Matches lack parallel vector clustering, characteristic of natural repetitive textures (brickwork, foliage, textiles)."
            )
        else:
            score = 92.0
            confidence = "high"
            explanation = (
                "Insufficient evidence for copy-move manipulation. "
                "Feature keypoint matching revealed no correlated duplicated regions."
            )

        return {
            "status": "success",
            "score": score,
            "confidence": confidence,
            "match_count": len(valid_pairs),
            "suspicious_clusters": clustered_count,
            "visualization_path": str(vis_output_path),
            "artifact_name": "copy_move.png",
            "explanation": explanation
        }

    except Exception as e:
        return {
            "status": "unavailable",
            "score": None,
            "confidence": "low",
            "explanation": f"Copy-move analysis encountered an error: {str(e)}",
            "visualization_path": None,
            "artifact_name": None
        }
