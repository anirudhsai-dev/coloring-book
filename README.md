# AI Coloring Book Generator & KDP Publishing Pipeline 🎨📚

An automated Python toolchain designed to generate AI image prompts, upscale generated line art, and assemble print-ready 8" x 11" coloring books and full-wrap covers for Amazon KDP (Kindle Direct Publishing) or physical printing.

---

## 🌟 Key Features

- **Categorized Prompt Generator**: Generates varied, item-focused prompts (fruits, snacks, drinks, food) with custom art style templates designed specifically for clean line-art coloring pages.
- **Automated Image Upscaling**: Connects to the **Automatic1111 Stable Diffusion WebUI API** to upscale images using models like `R-ESRGAN 4x+` for crisp printing resolution.
- **KDP-Compliant PDF Builder**: Converts upscaled images into an **8" x 11" (300 DPI)** PDF with appropriate printable safe areas and margins.
- **Full-Wrap Cover Creator**: Stitches front and back cover artwork into a full wrap cover PDF sized for KDP print specifications (17.32" x 11.25" at 300 DPI).

---

## 📁 Repository Structure

```text
.
├── categories.py          # Category dictionary (fruits, snacks, drinks, food)
├── prompt_templates.py   # Style templates for Midjourney/Stable Diffusion prompts
├── prompt_generator.py   # Core logic for unique prompt sequence generation
├── main.py               # Interactive CLI for prompt generation
├── upscale_images.py     # SD WebUI API script for R-ESRGAN image upscaling
├── create_pdf.py         # Assembles upscaled images into standard 8x11 PDF book
├── create_cover.py       # Assembles front & back images into full-wrap KDP cover
├── test_pytorch.py       # Utility script to check PyTorch & CUDA availability
├── requirements.txt      # Python dependencies
└── README.md             # Project documentation
```

---

## 🚀 Quick Start

### 1. Installation

Clone the repository and install the dependencies:

```bash
git clone https://github.com/YOUR_USERNAME/ai-coloring-book-generator.git
cd ai-coloring-book-generator
pip install -r requirements.txt
```

### 2. Generate Prompts

Run `main.py` to generate page prompts for Midjourney, Stable Diffusion, or Flux:

```bash
python main.py
```

### 3. Upscale Images

Ensure your Automatic1111 WebUI is running with API enabled (`--api` flag on `http://127.0.0.1:7860`). Place your raw images inside the `images/` directory and run:

```bash
python upscale_images.py
```

### 4. Build Book PDF

Place upscaled images into `upscaled_images/` and generate the printable PDF:

```bash
python create_pdf.py
```

### 5. Build Cover PDF

Place front and back cover images inside `coverend/` and generate the full wrap cover:

```bash
python create_cover.py
```

---

## 🛠️ Prerequisites & Setup

- **Python 3.9+**
- **Automatic1111 / SD WebUI** (with `--api` flag enabled) for image upscaling.
- **Pillow** & **Requests** (`requirements.txt`).

---

## 📜 License

This project is open-source and available under the [MIT License](LICENSE).
