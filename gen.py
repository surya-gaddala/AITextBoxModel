import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont
import random
import os
import shutil

# Set dataset paths
dataset_dir = "dataset"
image_dir = os.path.join(dataset_dir, "images")
label_dir = os.path.join(dataset_dir, "labels")
split_dirs = {
    "train": {"images": os.path.join(dataset_dir, "train", "images"), "labels": os.path.join(dataset_dir, "train", "labels")},
    "val": {"images": os.path.join(dataset_dir, "val", "images"), "labels": os.path.join(dataset_dir, "val", "labels")},
    "test": {"images": os.path.join(dataset_dir, "test", "images"), "labels": os.path.join(dataset_dir, "test", "labels")},
}

# Create necessary directories
os.makedirs(image_dir, exist_ok=True)
os.makedirs(label_dir, exist_ok=True)
for split in split_dirs.values():
    os.makedirs(split["images"], exist_ok=True)
    os.makedirs(split["labels"], exist_ok=True)

# Canvas size
WIDTH, HEIGHT = 700, 400
TEXTBOX_COLOR = (220, 220, 220)  # Light gray textbox

# Form fields
FIELDS = ["Name", "Email", "Phone", "Address", "City", "Country", "Zip Code"]
FONT_PATH = "arial.ttf"  # Update this with an available font

# Function to normalize bounding box coordinates for YOLO format
def normalize_bbox(x, y, w, h, img_w, img_h):
    return round(x / img_w, 6), round(y / img_h, 6), round(w / img_w, 6), round(h / img_h, 6)

# Generate dataset images
def generate_form_with_labels(image_index):
    image = Image.new("RGB", (WIDTH, HEIGHT), (255, 255, 255))
    draw = ImageDraw.Draw(image)
    
    # Load font with fallback
    try:
        font = ImageFont.truetype(FONT_PATH, 20)
    except:
        font = ImageFont.load_default()
    
    annotation_lines = []
    start_y = 50  # Starting Y position

    for field in random.sample(FIELDS, 4):  # Randomly pick 4 fields per form
        text_x = 50
        box_x = 200
        box_y = start_y
        box_width, box_height = 400, 40

        # Randomize label positions
        label_position = random.choice(["left", "top", "right", "bottom"])

        if label_position == "left":
            text_x = 50
            label_x, label_y = text_x, box_y + 10
        elif label_position == "top":
            label_x, label_y = box_x, box_y - 30
        elif label_position == "right":
            label_x, label_y = box_x + box_width + 10, box_y + 10
        elif label_position == "bottom":
            label_x, label_y = box_x, box_y + box_height + 5
        
        # Draw label text
        draw.text((label_x, label_y), f"{field}:", fill="black", font=font)
        
        # Draw textbox
        draw.rectangle([box_x, box_y, box_x + box_width, box_y + box_height], outline="black", fill=TEXTBOX_COLOR)
        
        # Get bounding box of the text
        try:
            bbox = font.getbbox(field)
            label_w, label_h = bbox[2] - bbox[0], bbox[3] - bbox[1]
        except AttributeError:  # Fallback for older versions of Pillow
            label_w, label_h = font.getsize(field)

        # Convert coordinates to YOLO format
        label_bbox = normalize_bbox(label_x + label_w / 2, label_y + label_h / 2, label_w, label_h, WIDTH, HEIGHT)
        textbox_bbox = normalize_bbox(box_x + box_width / 2, box_y + box_height / 2, box_width, box_height, WIDTH, HEIGHT)

        # Append annotations (class 0 = label, class 1 = textbox)
        annotation_lines.append(f"0 {label_bbox[0]} {label_bbox[1]} {label_bbox[2]} {label_bbox[3]}")
        annotation_lines.append(f"1 {textbox_bbox[0]} {textbox_bbox[1]} {textbox_bbox[2]} {textbox_bbox[3]}")

        start_y += 80  # Move to next field
    
    # Save image
    img_filename = f"{image_index}.png"
    img_path = os.path.join(image_dir, img_filename)
    image.save(img_path)

    # Save annotation file
    label_filename = f"{image_index}.txt"
    label_path = os.path.join(label_dir, label_filename)
    with open(label_path, "w") as f:
        f.write("\n".join(annotation_lines))

    print(f"Saved {img_filename} with annotations {label_filename}")

# Generate 150 dataset samples
for i in range(150):
    generate_form_with_labels(i)

# Split dataset into train (120), val (15), and test (15)
all_files = sorted(os.listdir(image_dir))
train_files = all_files[:120]
val_files = all_files[120:135]
test_files = all_files[135:]

# Move files to respective folders
def move_files(files, split_name):
    for file in files:
        shutil.move(os.path.join(image_dir, file), os.path.join(split_dirs[split_name]["images"], file))
        label_file = file.replace(".png", ".txt")
        shutil.move(os.path.join(label_dir, label_file), os.path.join(split_dirs[split_name]["labels"], label_file))

move_files(train_files, "train")
move_files(val_files, "val")
move_files(test_files, "test")

print("Dataset generation complete. Images and labels are split into train, val, and test sets.")
# Clean up original dataset directories