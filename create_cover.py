from PIL import Image, ImageOps
import os

# === SETTINGS ===
input_folder = "coverend"
fallback_folder_1 = "upscaled_images"
fallback_folder_2 = "images"
output_pdf_path = "coloring_book_full_wrap_8x11.pdf"

# Ensure folder exists
os.makedirs(input_folder, exist_ok=True)

# KDP-calculated wrap dimensions in inches (at 300 DPI)
TRIM_WIDTH_IN = 17.32
TRIM_HEIGHT_IN = 11.25

# Convert to pixels
TRIM_WIDTH = int(TRIM_WIDTH_IN * 300)   # 5196
TRIM_HEIGHT = int(TRIM_HEIGHT_IN * 300) # 3375
PAGE_SIZE = (TRIM_WIDTH, TRIM_HEIGHT)
half_width = TRIM_WIDTH // 2

# Helper to find valid image files in a folder
def get_images(folder):
    if not os.path.exists(folder):
        return []
    return sorted([
        os.path.join(folder, f) for f in os.listdir(folder)
        if f.lower().endswith((".png", ".jpg", ".jpeg"))
    ])

cover_images = get_images(input_folder)
fallback_images = get_images(fallback_folder_1) or get_images(fallback_folder_2)

# --- Resolve Front Cover ---
if len(cover_images) >= 1:
    front_cover_path = cover_images[0]
    print(f"Using front cover: {front_cover_path}")
    front_img = Image.open(front_cover_path).convert("RGB")
elif fallback_images:
    front_cover_path = fallback_images[0]
    print(f"No front cover found in '{input_folder}'. Falling back to: {front_cover_path}")
    front_img = Image.open(front_cover_path).convert("RGB")
else:
    print(f"No front cover or generated images found. Using blank canvas.")
    front_img = Image.new("RGB", (half_width, TRIM_HEIGHT), "white")

# --- Resolve Back Cover ---
if len(cover_images) >= 2:
    back_cover_path = cover_images[1]
    print(f"Using back cover: {back_cover_path}")
    back_img = Image.open(back_cover_path).convert("RGB")
elif len(fallback_images) >= 2:
    back_cover_path = fallback_images[1]
    print(f"No second cover image in '{input_folder}'. Falling back to: {back_cover_path}")
    back_img = Image.open(back_cover_path).convert("RGB")
else:
    print(f"No dedicated back cover found. Using clean white back cover.")
    back_img = Image.new("RGB", (half_width, TRIM_HEIGHT), "white")

# Resize each to fit half width and full height cleanly
resized_front = ImageOps.contain(front_img, (half_width, TRIM_HEIGHT))
resized_back = ImageOps.contain(back_img, (half_width, TRIM_HEIGHT))

# Create full wrap canvas
canvas = Image.new("RGB", PAGE_SIZE, "white")

# Paste back cover on the left, front cover on the right
canvas.paste(resized_back, ((half_width - resized_back.width) // 2, (TRIM_HEIGHT - resized_back.height) // 2))
canvas.paste(resized_front, (half_width + (half_width - resized_front.width) // 2, (TRIM_HEIGHT - resized_front.height) // 2))

# Save PDF at 300 DPI
canvas.save(output_pdf_path, "PDF", resolution=300.0)
print(f"✅ Correct-size full wrap PDF created: {output_pdf_path}")