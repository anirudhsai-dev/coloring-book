from PIL import Image, ImageOps
import os

# === SETTINGS ===
input_folder = "coverend"
output_pdf_path = "coloring_book_full_wrap_8x11.pdf"

# KDP-calculated wrap dimensions in inches (at 300 DPI)
TRIM_WIDTH_IN = 17.32
TRIM_HEIGHT_IN = 11.25

# Convert to pixels
TRIM_WIDTH = int(TRIM_WIDTH_IN * 300)   # 5196
TRIM_HEIGHT = int(TRIM_HEIGHT_IN * 300) # 3375
PAGE_SIZE = (TRIM_WIDTH, TRIM_HEIGHT)

# Get front and back cover
image_files = sorted([
    f for f in os.listdir(input_folder)
    if f.lower().endswith((".png", ".jpg", ".jpeg"))
])

front_cover_path = os.path.join(input_folder, image_files[0])
back_cover_path = os.path.join(input_folder, image_files[1])

# Open images
front_img = Image.open(front_cover_path).convert("RGB")
back_img = Image.open(back_cover_path).convert("RGB")

# Resize each to half of width and full height
half_width = TRIM_WIDTH // 2
resized_front = ImageOps.contain(front_img, (half_width, TRIM_HEIGHT))
resized_back = ImageOps.contain(back_img, (half_width, TRIM_HEIGHT))

# Create a white canvas of full wrap size
canvas = Image.new("RGB", PAGE_SIZE, "white")

# Paste back cover on the left, front on the right
canvas.paste(resized_back, (0, (TRIM_HEIGHT - resized_back.height) // 2))
canvas.paste(resized_front, (half_width, (TRIM_HEIGHT - resized_front.height) // 2))

# Save to PDF
canvas.save(output_pdf_path, resolution=300)
print(f"✅ Correct-size full wrap PDF created: {output_pdf_path}")
