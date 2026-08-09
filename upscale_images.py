import os
import requests
from PIL import Image
import base64
from io import BytesIO

# Configuration
WEBUI_API = "http://127.0.0.1:7860"
INPUT_FOLDER = "images"
OUTPUT_FOLDER = "upscaled_images"
UPSCALE_MODEL = "R-ESRGAN 4x+"  # You can also use "R-ESRGAN 4x+ Anime6B", etc.

# Ensure output folder exists
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

def encode_image(image_path):
    with open(image_path, "rb") as img_file:
        return base64.b64encode(img_file.read()).decode()

def decode_image(base64_str, save_path):
    image_data = base64.b64decode(base64_str)
    image = Image.open(BytesIO(image_data))
    image.save(save_path)

def upscale_image(image_path, output_path):
    base64_image = encode_image(image_path)
    payload = {
        "upscaling_resize": 4,  # scale factor (try 2, 3, or 4)
        "upscaler_1": UPSCALE_MODEL,
        "image": base64_image,
    }

    response = requests.post(f"{WEBUI_API}/sdapi/v1/extra-single-image", json=payload)
    if response.status_code == 200:
        result = response.json()
        decode_image(result["image"], output_path)
        print(f"✅ Upscaled: {os.path.basename(image_path)}")
    else:
        print(f"❌ Failed to upscale: {image_path}\n{response.text}")

# Process all PNGs (or add other formats)
for filename in os.listdir(INPUT_FOLDER):
    if filename.lower().endswith((".png", ".jpg", ".jpeg")):
        input_path = os.path.join(INPUT_FOLDER, filename)
        output_path = os.path.join(OUTPUT_FOLDER, filename)
        upscale_image(input_path, output_path)
