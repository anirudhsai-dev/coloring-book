from PIL import Image, ImageOps
import os

# === SETTINGS ===
input_folder = "upscaled_images"
output_pdf_path = "coloring_book.pdf"

# 8 x 11 inches at 300 DPI
TRIM_WIDTH = 2400
TRIM_HEIGHT = 3300
PAGE_SIZE = (TRIM_WIDTH, TRIM_HEIGHT)

# Padding in pixels (around all sides)
PADDING = 150
SAFE_WIDTH = TRIM_WIDTH - 2 * PADDING
SAFE_HEIGHT = TRIM_HEIGHT - 2 * PADDING
SAFE_AREA = (SAFE_WIDTH, SAFE_HEIGHT)

# Get and sort image files
image_files = sorted([
    f for f in os.listdir(input_folder)
    if f.lower().endswith((".png", ".jpg", ".jpeg"))
])

images = []

for filename in image_files:
    path = os.path.join(input_folder, filename)
    img = Image.open(path).convert("RGB")

    # Always resize image to fit within safe area
    resized_img = img.resize(ImageOps.contain(img, SAFE_AREA).size, Image.LANCZOS)

    # Create a white background canvas
    canvas = Image.new("RGB", PAGE_SIZE, "white")

    # Paste the resized image centered on the canvas
    x_offset = (TRIM_WIDTH - resized_img.width) // 2
    y_offset = (TRIM_HEIGHT - resized_img.height) // 2
    canvas.paste(resized_img, (x_offset, y_offset))

    images.append(canvas)

# Save all images as PDF
if images:
    images[0].save(output_pdf_path, save_all=True, append_images=images[1:], resolution=300)
    print(f"✅ PDF created with visible padding: {output_pdf_path}")
else:
    print("❌ No images found.")
