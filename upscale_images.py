# upscale_images.py

import base64
import os
import time
from io import BytesIO
from pathlib import Path
from typing import List, Union
import requests
from PIL import Image

# 1. API Configuration
DEFAULT_URL = "https://405bedfa7d7cde49c9.gradio.live"
BASE_URL = os.getenv("COLAB_API_URL", DEFAULT_URL).rstrip("/")
API_ENDPOINT = f"{BASE_URL}/sdapi/v1/extra-single-image"

# 2. Directory Defaults
INPUT_FOLDER = Path("images")
OUTPUT_FOLDER = Path("upscaled_images")
OUTPUT_FOLDER.mkdir(exist_ok=True)

# 3. Model Configuration
UPSCALE_MODEL = "R-ESRGAN 4x+ Anime6B"


def encode_image(image_path: Path) -> str:
    """Encode image file to base64 string."""
    with open(image_path, "rb") as img_file:
        return base64.b64encode(img_file.read()).decode("utf-8")


def upscale_image(image_path: Path, output_path: Path) -> bool:
    """Send a single image to the remote WebUI API for 4x magnification and edge-clean."""
    if output_path.exists():
        print(f"⏩ Skipping {image_path.name} (already exists)")
        return True

    print(f"Upscaling: {image_path.name}...")
    start_time = time.time()

    base64_image = encode_image(image_path)
    payload = {
        "upscaling_resize": 4,  # Upscales 512x640 to 2048x2560 (standard 300 DPI interior)
        "upscaler_1": UPSCALE_MODEL,
        "image": f"data:image/png;base64,{base64_image}",
    }

    try:
        response = requests.post(API_ENDPOINT, json=payload, timeout=180)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        print(f"❌ Failed to upscale {image_path.name}: {e}")
        return False

    result = response.json()
    raw_bytes = base64.b64decode(result["image"])

    # Load into Pillow and clean up interpolation haze
    img = Image.open(BytesIO(raw_bytes)).convert("L")

    # Clean thresholding: eliminate stray gray fuzz, keep true black contours
    cleaned = img.point(lambda p: 255 if p > 195 else 0).convert("RGB")
    cleaned.save(output_path, format="PNG")

    elapsed = round(time.time() - start_time, 1)
    print(f"✅ Upscaled & saved: {output_path.name} ({elapsed}s)")
    return True


def upscale_batch(target_files: List[Union[str, Path]]) -> int:
    """Batch entry point callable directly from main.py or other pipeline modules."""
    if not target_files:
        return 0

    print(f"\n--- Starting Upscaling Batch ({len(target_files)} files) via {BASE_URL} ---")
    processed = 0
    for item in target_files:
        src_path = Path(item)
        dest_path = OUTPUT_FOLDER / src_path.name
        if upscale_image(src_path, dest_path):
            processed += 1

    return processed


def main():
    """Standalone CLI entry point (scans entire images/ folder)."""
    image_files = sorted(
        [
            f
            for f in INPUT_FOLDER.iterdir()
            if f.suffix.lower() in [".png", ".jpg", ".jpeg"]
        ]
    )

    if not image_files:
        print(f"No source images found in '{INPUT_FOLDER}/'.")
        return

    print(f"Connecting to: {BASE_URL}")
    print(f"Found {len(image_files)} images in '{INPUT_FOLDER}/'...")

    completed = upscale_batch(image_files)
    print(f"\nFinished! Processed {completed}/{len(image_files)} images into '{OUTPUT_FOLDER}/'.")


if __name__ == "__main__":
    main()