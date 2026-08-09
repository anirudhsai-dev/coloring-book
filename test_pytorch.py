import torch
from ultralytics import YOLO

# Load YOLOv8 model
model = YOLO("yolov8n.pt")
print("YOLOv8 model loaded successfully!")
print("Torch version:", torch.__version__)
print("CUDA available:", torch.cuda.is_available())
print("GPU Name:", torch.cuda.get_device_name(0) if torch.cuda.is_available() else "No GPU detected")
