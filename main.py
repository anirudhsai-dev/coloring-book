# main.py

import base64
import io
import os
import re
import subprocess
import sys
import time
from pathlib import Path
import requests
from PIL import Image

from prompt_generator import PromptGenerator

# Remote GPU API Endpoint
DEFAULT_URL = "https://405bedfa7d7cde49c9.gradio.live"
BASE_URL = os.getenv("COLAB_API_URL", DEFAULT_URL).rstrip("/")
TXT2IMG_URL = f"{BASE_URL}/sdapi/v1/txt2img"
UPSCALE_URL = f"{BASE_URL}/sdapi/v1/extra-single-image"

# Directory Structure
IMAGES_DIR = Path("images")
UPSCALED_DIR = Path("upscaled_images")
COVER_DIR = Path("coverend")

IMAGES_DIR.mkdir(exist_ok=True)
UPSCALED_DIR.mkdir(exist_ok=True)
COVER_DIR.mkdir(exist_ok=True)

NEGATIVE_PROMPT = (
    "dots, spots, splatter, floating particles, debris, bubbles, splashes, droplets, "
    "speckled, noise, texture, patterns, small shapes, intricate, detailed, shading, "
    "gradients, shadows, grayscale, color, background elements, wallpaper, frame, border"
)


def get_next_page_number() -> int:
    """Find the highest existing page number across raw and upscaled directories."""
    files = list(IMAGES_DIR.glob("page_*.png")) + list(UPSCALED_DIR.glob("page_*.png"))
    highest = 0
    for f in files:
        match = re.search(r"page_(\d+)", f.stem)
        if match:
            num = int(match.group(1))
            if num > highest:
                highest = num
    return highest + 1


# ==========================================
# STEP 2: GENERATE IMAGES
# ==========================================
def generate_image(prompt: str, output_path: Path) -> bool:
    payload = {
        "prompt": prompt,
        "negative_prompt": NEGATIVE_PROMPT,
        "steps": 24,
        "sampler_name": "Euler a",
        "cfg_scale": 6.5,
        "width": 512,
        "height": 640,
        "seed": -1,
    }

    start_time = time.time()
    try:
        response = requests.post(TXT2IMG_URL, json=payload, timeout=120)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        print(f"❌ Error during generation: {e}")
        return False

    data = response.json()
    raw_bytes = base64.b64decode(data["images"][0])

    # Thresholding filter: clean binary black and white
    img = Image.open(io.BytesIO(raw_bytes)).convert("L")
    binarized = img.point(lambda p: 255 if p > 200 else 0).convert("RGB")
    binarized.save(output_path, format="PNG")

    elapsed = round(time.time() - start_time, 1)
    print(f"✅ Generated: {output_path.name} ({elapsed}s)")
    return True


# ==========================================
# STEP 3: UPSCALE IMAGES
# ==========================================
def upscale_batch(target_files: list):
    print("\n--- [Step 3/5] Upscaling to 300 DPI (4x R-ESRGAN) ---")
    for img_path in target_files:
        output_path = UPSCALED_DIR / img_path.name
        if output_path.exists():
            print(f"⏩ Skipping {img_path.name} (already upscaled)")
            continue

        print(f"Upscaling {img_path.name}...")
        start_time = time.time()

        with open(img_path, "rb") as f:
            encoded = base64.b64encode(f.read()).decode("utf-8")

        payload = {
            "upscaling_resize": 4,
            "upscaler_1": "R-ESRGAN 4x+ Anime6B",
            "image": f"data:image/png;base64,{encoded}",
        }

        try:
            res = requests.post(UPSCALE_URL, json=payload, timeout=120)
            res.raise_for_status()
            data = res.json()
            raw_bytes = base64.b64decode(data["image"])

            # Clean thresholding after 4x expansion
            img = Image.open(io.BytesIO(raw_bytes)).convert("L")
            binarized = img.point(lambda p: 255 if p > 200 else 0).convert("RGB")
            binarized.save(output_path, format="PNG")

            elapsed = round(time.time() - start_time, 1)
            print(f"✅ Upscaled & saved: {output_path.name} ({elapsed}s)")
        except requests.exceptions.RequestException as e:
            print(f"❌ Upscale error on {img_path.name}: {e}")


# ==========================================
# STEPS 4 & 5: SUBPROCESS COMPILATION
# ==========================================
def run_script(script_name: str, step_label: str):
    print(f"\n--- {step_label} (Executing {script_name}) ---")
    if not Path(script_name).exists():
        print(f"⚠️ Script '{script_name}' not found. Skipping.")
        return

    result = subprocess.run([sys.executable, script_name])
    if result.returncode == 0:
        print(f"✅ Finished {script_name} successfully.")
    else:
        print(f"❌ Error while running {script_name} (exit code: {result.returncode}).")


# ==========================================
# MASTER PIPELINE ENTRY
# ==========================================
def main():
    print("=" * 50)
    print("      KDP ALL-IN-ONE AUTOMATED BOOK BUILDER       ")
    print("=" * 50)

    topic = input("\nEnter coloring book topic (e.g. 'jungle animals for kids'): ").strip()
    if not topic:
        topic = "jungle animals for kids"

    pages_input = input("Enter number of pages (default 30): ").strip()
    num_pages = int(pages_input) if pages_input.isdigit() else 30

    print(f"\nConfiguration: Topic='{topic}' | Pages={num_pages}")
    print(f"API Endpoint: {BASE_URL}")

    # STEP 1: Generate Prompts (with persistent history deduplication)
    print("\n--- [Step 1/5] Generating Prompts & Checking Deduplication ---")
    generator = PromptGenerator(topic)
    prompts_data = generator.generate_prompts(num_pages=num_pages)

    # STEP 2: Generate Raw Images
    print(f"\n--- [Step 2/5] Generating {len(prompts_data)} Raw Images via Colab ---")
    start_index = get_next_page_number()
    generated_files = []

    for idx, (item_name, prompt) in enumerate(prompts_data, start=start_index):
        filename = f"page_{idx:03d}.png"
        file_path = IMAGES_DIR / filename
        current_step = idx - start_index + 1
        print(f"Generating [{current_step}/{num_pages}]: {item_name}")

        if generate_image(prompt, file_path):
            generated_files.append(file_path)

    # STEP 3: Upscale Generated Batch
    upscale_batch(generated_files)

    # STEP 4: Build Interior PDF
    run_script("create_pdf.py", "[Step 4/5] Building Printable Interior PDF")

    # STEP 5: Build Wrap Cover PDF
    run_script("create_cover.py", "[Step 5/5] Building Full Wrap Cover PDF")

    print("\n" + "=" * 50)
    print("🎉 ALL 5 PIPELINE STEPS COMPLETED!")
    print(f"• Raw Images: {IMAGES_DIR}/")
    print(f"• Upscaled Pages: {UPSCALED_DIR}/")
    print("• Check project root for your interior and cover PDF outputs.")
    print("=" * 50)


if __name__ == "__main__":
    main()