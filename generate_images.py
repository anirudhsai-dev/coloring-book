import base64
import io
import time
from pathlib import Path
import requests
from PIL import Image

# 1. Pipeline imports
from prompt_generator import PromptGenerator
from categories import categories

# 2. Remote API endpoint
BASE_URL = "https://405bedfa7d7cde49c9.gradio.live".rstrip('/')
API_URL = f"{BASE_URL}/sdapi/v1/txt2img"

# Local output directory for images
OUTPUT_DIR = Path("images")
OUTPUT_DIR.mkdir(exist_ok=True)

# Strict negative prompt to strip shading, gray textures, sketches, and clutter
NEGATIVE_PROMPT = (
    "color, grayscale, gray, shading, shadows, gradients, realistic, photograph, "
    "numbers, digits, letters, text, font, watermark, signature, sketch lines, "
    "fine details, tiny lines, crosshatching, complex patterns, frame, border, "
    "split screen, multiple characters, collage, noisy, low quality"
)

def generate_image(prompt: str, filename: str):
    payload = {
        "prompt": prompt,
        "negative_prompt": NEGATIVE_PROMPT,
        "steps": 26,
        "sampler_name": "DPM++ 2M Karras",  # Sharp, clean vector edge rendering
        "cfg_scale": 8.5,                   # Forces strict outline adherence
        "width": 512,
        "height": 640,                      # 8.5x11 portrait ratio with footer room
        "seed": -1,
    }

    print(f"\nGenerating: {filename}...")
    print(f"Prompt: {prompt}")
    start_time = time.time()

    try:
        response = requests.post(API_URL, json=payload, timeout=120)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        print(f"Error communicating with Colab GPU: {e}")
        return False

    data = response.json()
    image_base64 = data["images"][0]

    # Decode and binarize to ensure pure black lines on pure white canvas
    img = Image.open(io.BytesIO(base64.b64decode(image_base64))).convert("L")
    
    # Thresholding: anything lighter than 200 becomes 255 (white), rest becomes 0 (black)
    binarized = img.point(lambda p: 255 if p > 200 else 0).convert("RGB")
    
    output_path = OUTPUT_DIR / filename
    binarized.save(output_path, format="PNG")

    elapsed = round(time.time() - start_time, 1)
    print(f"Saved: {output_path} ({elapsed}s)")
    return True

def main():
    selected_categories = list(categories.keys())
    template_id = 1
    num_pages = 30

    generator = PromptGenerator(selected_categories=selected_categories, prompt_id=template_id)
    prompts = generator.generate_prompt(num_pages=num_pages)

    print(f"Connecting to Colab GPU at: {BASE_URL}")
    print(f"Processing {len(prompts)} pages...")

    success_count = 0
    for i, prompt in enumerate(prompts, start=1):
        filename = f"page_{i:03d}.png"
        output_path = OUTPUT_DIR / filename

        # Skip existing files to save GPU time
        if output_path.exists():
            print(f"Skipping {filename} (already exists)")
            success_count += 1
            continue

        if generate_image(prompt, filename):
            success_count += 1

    print(f"\nFinished! Processed {success_count}/{len(prompts)} images into '{OUTPUT_DIR}/'.")

if __name__ == "__main__":
    main()