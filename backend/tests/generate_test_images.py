"""Generates reproducible synthetic test images for VisionGuard automated testing."""

from pathlib import Path
import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont

TEST_DIR = Path(__file__).resolve().parent / "test_images"
TEST_DIR.mkdir(parents=True, exist_ok=True)


def generate_images():
    # 1. Clean synthetic natural image (gradient with circles)
    clean_path = TEST_DIR / "clean_synthetic.png"
    img_clean = np.zeros((400, 400, 3), dtype=np.uint8)
    for y in range(400):
        for x in range(400):
            img_clean[y, x] = [int(x / 400 * 255), int(y / 400 * 255), 180]
    cv2.circle(img_clean, (200, 200), 60, (50, 200, 50), -1)
    cv2.imwrite(str(clean_path), img_clean)

    # 2. Image containing text (for OCR and NLP claim verification)
    text_path = TEST_DIR / "text_claim.png"
    pil_text = Image.new("RGB", (600, 300), color=(255, 255, 255))
    draw = ImageDraw.Draw(pil_text)
    draw.text((30, 80), "The Eiffel Tower is in Paris, France.", fill=(0, 0, 0))
    draw.text((30, 140), "Inaugurated in 1889 as a world landmark.", fill=(50, 50, 50))
    pil_text.save(text_path)

    # 3. Image with duplicated region (copy-move forgery)
    copymove_path = TEST_DIR / "copy_move_forgery.png"
    cm_img = np.ones((500, 500, 3), dtype=np.uint8) * 220
    # Add unique high-entropy texture pattern
    for i in range(10):
        cv2.rectangle(cm_img, (50 + i*5, 50 + i*5), (120, 120), (30*i % 255, 60*i % 255, 90*i % 255), 2)
    # Clone the exact patch from (50, 50) to (300, 300)
    patch = cm_img[40:130, 40:130].copy()
    cm_img[300:390, 300:390] = patch
    cv2.imwrite(str(copymove_path), cm_img)

    # 4. JPEG recompressed image (for ELA verification)
    jpeg_path = TEST_DIR / "recompressed_ela.jpg"
    base_img = img_clean.copy()
    # Insert high-contrast uncompressed box to trigger ELA differential
    cv2.rectangle(base_img, (50, 50), (150, 150), (255, 0, 0), -1)
    cv2.imwrite(str(jpeg_path), base_img, [cv2.IMWRITE_JPEG_QUALITY, 70])

    print(f"Generated test images in {TEST_DIR}")


if __name__ == "__main__":
    generate_images()
