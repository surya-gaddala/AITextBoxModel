import os
import time
import cv2
import torch
import numpy as np
import pyautogui
import pytesseract
import logging
import tkinter as tk
from tkinter import filedialog
from threading import Thread
from ultralytics import YOLO
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager

# ================== Configuration ======================
BASE_DIR = r"C:\DFT\DFT\Repo\AIML\Empty Text Box(Label)"
BOX_DIR = os.path.join(BASE_DIR, "Box Detection")

DEFAULT_MODEL_PATH = os.path.join(BASE_DIR, r"runs\detect\train2\weights\best.pt")
DEFAULT_INPUT_PATH = os.path.join(BASE_DIR, "input.txt")
TESSERACT_PATH = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
SCREENSHOT_PATH = os.path.join(BASE_DIR, "webpage.png")
TARGET_URL = "https://testautomationpractice.blogspot.com/"

# ================== Setup ======================
logging.basicConfig(level=logging.INFO, format="🔹 %(message)s")
pytesseract.pytesseract.tesseract_cmd = TESSERACT_PATH

chrome_options = Options()
chrome_options.add_argument("--start-maximized")  # Start maximized
chrome_options.add_argument("--disable-blink-features=AutomationControlled")

# ================== WebDriver ======================
def init_webdriver():
    try:
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=chrome_options)
        
        # Set the window to be maximized initially
        driver.maximize_window()
        logging.info("Browser window maximized.")

        # Ensuring the browser size is set correctly
        driver.set_window_size(1200, 800)  # Ensure stable size during test
        return driver
    except Exception as e:
        logging.error(f"WebDriver initialization failed: {e}")
        exit(1)

# ================== Window Management ======================
def ensure_maximized_window(driver):
    try:
        driver.maximize_window()
        logging.info("Window size reset to maximized.")
    except Exception as e:
        logging.warning(f"Failed to reset window size: {e}")

# ================== Screenshot ======================
def take_fullpage_screenshot(driver, path):
    try:
        total_width = driver.execute_script("return document.body.scrollWidth")
        total_height = driver.execute_script("return document.body.scrollHeight")
        driver.set_window_size(total_width, total_height)  # Set the window size to the full height of the page
        time.sleep(2)
        driver.save_screenshot(path)
        logging.info(f"📸 Full-page screenshot saved: {path}")
    except Exception as e:
        logging.error(f"Screenshot capture failed: {e}")

# ================== Load Model ======================
def load_model(path):
    try:
        return YOLO(path)
    except Exception as e:
        logging.error(f"YOLO model load failed: {e}")
        exit(1)

# ================== Extract Detections ======================
def extract_detections(model, image):
    results = model(image)
    labels, boxes = {}, []
    debug_img = image.copy()

    for result in results:
        for box in result.boxes.data:
            x1, y1, x2, y2, conf, class_id = map(int, box[:6])
            roi = image[y1:y2, x1:x2]
            roi_gray = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)
            roi_thresh = cv2.threshold(roi_gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1]
            text = pytesseract.image_to_string(roi_thresh, config='--psm 7').strip()
            normalized_text = ''.join(filter(str.isalnum, text.lower()))

            logging.info(f"🔍 Detected Class {class_id}: '{text}'")

            if class_id == 0:
                labels[normalized_text] = (x1, y1, x2, y2)
                color, label = (0, 255, 0), text  # Green for detected labels
            else:
                boxes.append((x1, y1, x2, y2))
                color, label = (255, 0, 0), "Textbox"  # Red for textboxes

            cv2.rectangle(debug_img, (x1, y1), (x2, y2), color, 2)
            cv2.putText(debug_img, label, (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)

    # Save the image with highlighted labels
    debug_img_path = os.path.join(BOX_DIR, "detection_highlighted.png")
    cv2.imwrite(debug_img_path, debug_img)
    logging.info(f"🧪 Detection highlighted image saved: {debug_img_path}")

    return labels, boxes

# ================== Input Reader ======================
def read_input_file(path):
    data = {}
    try:
        with open(path, 'r') as file:
            for line in file:
                if "=" in line:
                    key, value = line.strip().split("=", 1)
                    normalized_key = ''.join(filter(str.isalnum, key.lower()))
                    data[normalized_key] = value
    except FileNotFoundError:
        logging.error(f"Input file not found: {path}")
        exit(1)
    return data

# ================== Match Textbox ======================
def find_closest_textbox(label_coords, textboxes):
    lx1, ly1, lx2, ly2 = label_coords
    closest_box, min_dist = None, float('inf')

    for tx1, ty1, tx2, ty2 in textboxes:
        vertical_dist = abs(ly2 - ty1)
        horizontal_dist = abs((lx1 + lx2) // 2 - (tx1 + tx2) // 2)
        dist = vertical_dist + horizontal_dist
        if dist < min_dist:
            min_dist = dist
            closest_box = (tx1, ty1, tx2, ty2)

    return closest_box

# ================== Scroll to Element ======================
def scroll_to(driver, y):
    try:
        driver.execute_script(f"window.scrollTo(0, {y})")  # Scroll to the vertical position
        time.sleep(0.5)
    except Exception as e:
        logging.warning(f"Scroll failed: {e}")

# ================== Input Automator ======================
def enter_text_at(driver, label_bbox, text):
    x1, y1, x2, y2 = label_bbox
    # Calculate the center of the label's bounding box
    center_x, center_y = (x1 + x2) // 2, (y1 + y2) // 2

    # Move the mouse to the label's center
    pyautogui.moveTo(center_x, center_y, duration=0.5)
    pyautogui.click()  # Click on the label's position to focus on it

    # Allow some time for the click action to register
    time.sleep(0.3)

    # Write the text at the label's position
    pyautogui.write(text, interval=0.1)

    logging.info(f"✅ Entered '{text}' at label position ({center_x}, {center_y})")

    return center_x, center_y

# ================== Main Executor ======================
def run_automation(model_path, input_path):
    driver = init_webdriver()
    driver.get(TARGET_URL)
    time.sleep(3)

    take_fullpage_screenshot(driver, SCREENSHOT_PATH)
    model = load_model(model_path)

    image = cv2.imread(SCREENSHOT_PATH)
    if image is None:
        logging.error("Failed to load screenshot image.")
        driver.quit()
        return

    labels, boxes = extract_detections(model, image)
    label_data = read_input_file(input_path)

    for target_label, input_value in label_data.items():
        matched_label_coords = labels.get(target_label)

        if matched_label_coords:
            textbox_coords = find_closest_textbox(matched_label_coords, boxes)
            if textbox_coords:
                cx, cy = enter_text_at(driver, textbox_coords, input_value)
                logging.info(f"✅ Entered '{input_value}' at screen position ({cx}, {cy})")
            else:
                logging.warning(f"⚠️ No textbox found near label '{target_label}'")
        else:
            logging.warning(f"⚠️ Target label '{target_label}' not found.")

    final_ss_path = os.path.join(BOX_DIR, "after_entry.png")
    driver.save_screenshot(final_ss_path)
    logging.info(f"📸 Screenshot after entry saved: {final_ss_path}")
    driver.quit()
    logging.info("✅ Process completed successfully.")

# ================== GUI ======================
def start_gui():
    def run_threaded():
        Thread(target=lambda: run_automation(model_path.get(), input_path.get())).start()

    app = tk.Tk()
    app.title("YOLO Form Filler GUI")
    app.geometry("500x250")

    model_path = tk.StringVar(value=DEFAULT_MODEL_PATH)
    input_path = tk.StringVar(value=DEFAULT_INPUT_PATH)

    # Function to allow file selection for the model
    def select_model():
        file_path = filedialog.askopenfilename(filetypes=[("Model Files", "*.pt")])
        model_path.set(file_path)

    # Function to allow file selection for the input file
    def select_input():
        file_path = filedialog.askopenfilename(filetypes=[("Text Files", "*.txt")])
        input_path.set(file_path)

    tk.Button(app, text="Select Model", bg="blue", fg="white", command=select_model).pack(pady=5)
    tk.Button(app, text="Select Input File", bg="blue", fg="white", command=select_input).pack(pady=5)
    tk.Button(app, text="Run Automation", bg="green", fg="white", command=run_threaded).pack(pady=20)

    app.mainloop()

# ================== Start GUI ======================
start_gui()
