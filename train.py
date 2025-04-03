from ultralytics import YOLO

# Load YOLO model (using a pre-trained model for transfer learning)
model = YOLO("yolov8n.pt")  

# Train the model
results = model.train(data="dataset/data.yaml", epochs=50, batch=16, imgsz=640)
