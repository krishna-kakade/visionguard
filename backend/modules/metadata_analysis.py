"""EXIF and Metadata Analysis module for VisionGuard.

Inspects embedded image metadata, camera information, editing software traces,
and geolocation without unfairly categorizing stripped metadata as fake.
"""

from pathlib import Path
from typing import Dict, Any
from PIL import Image, ExifTags


def analyze_metadata(file_path: Path) -> Dict[str, Any]:
    """Extracts and evaluates EXIF headers, camera parameters, and software tags."""
    try:
        with Image.open(file_path) as img:
            format_name = img.format or file_path.suffix.lstrip(".").upper()
            width, height = img.size
            mode = img.mode

            raw_exif = img.getexif()
            has_exif = bool(raw_exif and len(raw_exif) > 0)

            exif_dict: Dict[str, Any] = {}
            camera_make = None
            camera_model = None
            software = None
            datetime_taken = None
            has_gps = False

            if has_exif:
                for tag_id, value in raw_exif.items():
                    tag_name = ExifTags.TAGS.get(tag_id, str(tag_id))
                    # Convert bytes to string safely
                    if isinstance(value, bytes):
                        try:
                            value = value.decode("utf-8", errors="ignore").strip()
                        except Exception:
                            value = str(value)
                    exif_dict[tag_name] = str(value)

                camera_make = exif_dict.get("Make")
                camera_model = exif_dict.get("Model")
                software = exif_dict.get("Software")
                datetime_taken = exif_dict.get("DateTime") or exif_dict.get("DateTimeOriginal")

                # Check GPS IFD if available
                gps_ifd = raw_exif.get_ifd(ExifTags.IFD.GPSInfo) if hasattr(raw_exif, "get_ifd") else None
                if gps_ifd:
                    has_gps = True

        # Responsible evaluation:
        # 1. Camera metadata intact (Make + Model + Timestamp) -> High authenticity provenance
        # 2. Software indicates editor (Photoshop, GIMP) -> Suspicious provenance
        # 3. Stripped metadata -> Very common due to social media platforms (Twitter, WhatsApp), so neutral/insufficient evidence!
        
        software_lower = (software or "").lower()
        editing_tools = ["photoshop", "gimp", "canva", "lightroom", "paint.net", "corel"]
        detected_editor = next((tool for tool in editing_tools if tool in software_lower), None)

        if detected_editor:
            score = 40.0
            confidence = "high"
            explanation = (
                f"Metadata indicates image was processed or saved using image editing software: '{software}'. "
                "This suggests digital modification or graphic composition."
            )
        elif camera_make and camera_model:
            score = 90.0
            confidence = "high"
            explanation = (
                f"Original hardware metadata found: Captured with {camera_make} {camera_model}. "
                "Contains consistent camera capture parameters."
            )
        elif has_exif:
            score = 75.0
            confidence = "medium"
            explanation = "Partial EXIF metadata present, but camera hardware provenance is unspecified."
        else:
            score = 60.0
            confidence = "low"
            explanation = (
                "No EXIF metadata found. Most social media platforms and messaging apps "
                "automatically strip metadata for privacy reasons. Stripped metadata alone does not indicate manipulation."
            )

        return {
            "status": "success",
            "score": score,
            "confidence": confidence,
            "has_exif": has_exif,
            "format": format_name,
            "dimensions": f"{width}x{height}",
            "color_mode": mode,
            "camera_make": camera_make,
            "camera_model": camera_model,
            "software": software,
            "timestamp": datetime_taken,
            "has_gps": has_gps,
            "explanation": explanation,
            "raw_tags_count": len(exif_dict)
        }

    except Exception as e:
        return {
            "status": "unavailable",
            "score": None,
            "confidence": "low",
            "has_exif": False,
            "explanation": f"Unable to parse image metadata: {str(e)}",
            "raw_tags_count": 0
        }
