"""Copy-Move Forgery Detection module for VisionGuard.

Uses keypoint feature matching (ORB/SIFT) with spatial separation constraints
and shift-vector clustering to identify cloned or duplicated regions.
"""

from pathlib import Path
from typing import Dict, Any, List, Tuple
import cv2
import numpy as np


def detect_copy_move(
    image_path: Path,
    output_dir: Path,
    min_spatial_distance: float = 35.0,
    max_features: int = 1500
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
            detector = cv2.SIFT_create(nfeatures=max_features)
            matcher = cv2.BFMatcher(cv2.NORM_L2)
            is_sift = True
        except Exception:
            detector = cv2.ORB_create(nfeatures=max_features)
            matcher = cv2.BFMatcher(cv2.NORM_HAMMING)

        keypoints, descriptors = detector.detectAndCompute(gray, None)

        if descriptors is None or len(keypoints) < 15:
            # Draw standard clean visual
            cv2.imwrite(str(vis_output_path), img_bgr)
            return {
                "status": "success",
                "score": 75.0,
                "confidence": "low",
                "match_count": 0,
                "suspicious_clusters": 0,
                "explanation": "Insufficient feature keypoints detected for copy-move analysis (e.g. flat color or low texture).",
                "visualization_path": str(vis_output_path),
                "artifact_name": "copy_move.png"
            }

        # Find 2 nearest neighbors for each descriptor
        knn_matches = matcher.knnMatch(descriptors, descriptors, k=3)

        valid_pairs: List[Tuple[cv2.KeyPoint, cv2.KeyPoint, np.ndarray]] = []
        vectors: List[Tuple[float, float]] = []

        ratio_thresh = 0.72 if is_sift else 0.75

        for match_group in knn_matches:
            if len(match_group) < 2:
                continue
            
            # The first match (match_group[0]) is almost always self with distance 0.
            # Compare match_group[1] (first actual neighbor) or match_group[2]
            best = match_group[1] if len(match_group) >= 2 and match_group[0].queryIdx == match_group[0].trainIdx else match_group[0]
            
            if best.queryIdx == best.trainIdx:
                continue

            kp1 = keypoints[best.queryIdx]
            kp2 = keypoints[best.trainIdx]

            pt1 = np.array(kp1.pt)
            pt2 = np.array(kp2.pt)
            spatial_dist = np.linalg.norm(pt1 - pt2)

            # Spatial distance filter: must be distinct locations, not adjacent noise
            if spatial_dist > min_spatial_distance:
                # Descriptor quality check
                if len(match_group) >= 3:
                    if best.distance < ratio_thresh * match_group[2].distance:
                        valid_pairs.append((kp1, kp2, pt2 - pt1))
                        vectors.append((float(pt2[0] - pt1[0]), float(pt2[1] - pt1[1])))
                else:
                    valid_pairs.append((kp1, kp2, pt2 - pt1))
                    vectors.append((float(pt2[0] - pt1[0]), float(pt2[1] - pt1[1])))

        # Shift-vector clustering: copy-move tampering usually has multiple matches with identical translation displacement vectors
        clustered_count = 0
        clustered_pairs = []
        
        if len(vectors) >= 4:
            vec_arr = np.array(vectors)
            # Find vector consistency: displacement angle and magnitude
            angles = np.arctan2(vec_arr[:, 1], vec_arr[:, 0])
            mags = np.linalg.norm(vec_arr, axis=1)

            for i in range(len(vectors)):
                similar = 0
                for j in range(len(vectors)):
                    if i != j:
                        angle_diff = abs(angles[i] - angles[j])
                        mag_diff = abs(mags[i] - mags[j])
                        if angle_diff < 0.15 and mag_diff < 20:
                            similar += 1
                if similar >= 3:
                    clustered_count += 1
                    clustered_pairs.append(valid_pairs[i])

        # Visualization output
        vis_img = img_bgr.copy()
        
        # Draw all valid candidate lines in faint cyan, clustered duplicates in bright orange/red
        for kp1, kp2, _ in valid_pairs[:40]:
            p1 = (int(kp1.pt[0]), int(kp1.pt[1]))
            p2 = (int(kp2.pt[0]), int(kp2.pt[1]))
            cv2.line(vis_img, p1, p2, (230, 216, 0), 1, cv2.LINE_AA)
            cv2.circle(vis_img, p1, 3, (255, 200, 0), -1)
            cv2.circle(vis_img, p2, 3, (255, 200, 0), -1)

        for kp1, kp2, _ in clustered_pairs:
            p1 = (int(kp1.pt[0]), int(kp1.pt[1]))
            p2 = (int(kp2.pt[0]), int(kp2.pt[1]))
            cv2.line(vis_img, p1, p2, (0, 0, 255), 2, cv2.LINE_AA)
            cv2.circle(vis_img, p1, 5, (0, 70, 255), -1)
            cv2.circle(vis_img, p2, 5, (0, 70, 255), -1)

        cv2.imwrite(str(vis_output_path), vis_img)

        # Decide score responsibly
        if clustered_count >= 6:
            score = 30.0
            confidence = "high"
            explanation = (
                f"Suspicious repeated structures detected: {clustered_count} aligned feature pairs share consistent spatial displacement. "
                "Strong indication of copy-move cloning or object duplication."
            )
        elif len(valid_pairs) > 15:
            score = 65.0
            confidence = "medium"
            explanation = (
                f"Detected {len(valid_pairs)} recurring keypoint pairs across the image. "
                "May indicate natural repetitive textures (e.g. foliage, waves, brickwork) rather than deliberate manipulation."
            )
        else:
            score = 90.0
            confidence = "high"
            explanation = (
                "Insufficient evidence for copy-move manipulation. "
                "Feature matching revealed no correlated duplicated regions."
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
