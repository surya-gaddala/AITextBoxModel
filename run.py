# import time
# import cv2
# import torch
# import numpy as np
# import pyautogui
# import pytesseract
# from ultralytics import YOLO
# from selenium import webdriver
# from selenium.webdriver.chrome.service import Service
# from selenium.webdriver.chrome.options import Options
# from webdriver_manager.chrome import ChromeDriverManager

# # Configure Tesseract OCR
# pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

# # Load trained YOLO model
# MODEL_PATH = r"C:\DFT\DFT\Repo\AIML\Empty Text Box(Label)\runs\detect\train2\weights\best.pt"

# # Start Selenium WebDriver
# chrome_options = Options()
# chrome_options.add_argument("--start-maximized")
# chrome_options.add_argument("--disable-blink-features=AutomationControlled")

# try:
#     service = Service(ChromeDriverManager().install())
#     driver = webdriver.Chrome(service=service, options=chrome_options)
# except Exception as e:
#     print(f"❌ Error initializing WebDriver: {e}")
#     exit(1)

# # Open the webpage
# URL = "https://testautomationpractice.blogspot.com/"
# driver.get(URL)
# time.sleep(3)

# # Capture screenshot
# screenshot_path = "webpage.png"
# driver.save_screenshot(screenshot_path)

# # Load YOLO Model
# try:
#     model = YOLO(MODEL_PATH)
# except Exception as e:
#     print(f"❌ Error loading YOLO model: {e}")
#     driver.quit()
#     exit(1)

# # Detect elements
# image = cv2.imread(screenshot_path)
# results = model(image)

# detected_labels = {}  # Store detected labels
# detected_boxes = []   # Store text boxes
# debug_image = image.copy()  # Image for debugging

# for result in results:
#     for box in result.boxes.data:
#         x1, y1, x2, y2, conf, class_id = map(int, box[:6])
#         cropped_region = image[y1:y2, x1:x2]

#         # Improve OCR accuracy
#         detected_text = pytesseract.image_to_string(cropped_region, config='--psm 7').strip()
#         detected_text_cleaned = ''.join(filter(str.isalnum, detected_text.lower()))  # Normalize text

#         if class_id == 0:  # Label
#             detected_labels[detected_text_cleaned] = (x1, y1, x2, y2)
#             cv2.rectangle(debug_image, (x1, y1), (x2, y2), (0, 255, 0), 2)
#             cv2.putText(debug_image, f"{detected_text} ({conf:.2f})", (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

#         elif class_id == 1:  # Textbox
#             detected_boxes.append((x1, y1, x2, y2))
#             cv2.rectangle(debug_image, (x1, y1), (x2, y2), (255, 0, 0), 2)
#             cv2.putText(debug_image, "Textbox", (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 0), 2)

# # Save debug image
# cv2.imwrite("detection_debug.png", debug_image)

# # Log detected labels
# print("\n🔍 Detected Labels:")
# for label, bbox in detected_labels.items():
#     print(f"  ➜ {label}: {bbox}")

# print("\n🔍 Detected Text Boxes:")
# for i, box in enumerate(detected_boxes):
#     print(f"  ➜ Box {i + 1}: {box}")

# # Find best match for "Name" label
# username_box = None
# for label, (lx1, ly1, lx2, ly2) in detected_labels.items():
#     if "name" in label:  # Match normalized label
#         closest_textbox = None
#         min_distance = float('inf')

#         for (tx1, ty1, tx2, ty2) in detected_boxes:
#             distance = abs(ly2 - ty1)  # Check vertical distance
#             if distance < min_distance:
#                 min_distance = distance
#                 closest_textbox = (tx1, ty1, tx2, ty2)

#         username_box = closest_textbox
#         break

# # Function to highlight detected field
# def highlight_and_capture(field_name, bbox, step):
#     x1, y1, x2, y2 = bbox
#     highlighted_image = image.copy()
#     cv2.rectangle(highlighted_image, (x1, y1), (x2, y2), (0, 255, 255), 3)
#     cv2.putText(highlighted_image, field_name, (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 255), 2)
#     screenshot_filename = f"screenshot_step_{step}.png"
#     cv2.imwrite(screenshot_filename, highlighted_image)
#     print(f"📸 Screenshot saved: {screenshot_filename}")

# # Enter text in Username field
# if username_box:
#     tx1, ty1, tx2, ty2 = username_box
#     center_x, center_y = (tx1 + tx2) // 2, (ty1 + ty2) // 2

#     highlight_and_capture("Entering Name", username_box, step=1)

#     pyautogui.moveTo(center_x, center_y, duration=0.5)
#     pyautogui.click()
#     time.sleep(0.5)
#     pyautogui.write("TestUser123", interval=0.1)

#     highlight_and_capture("Entered Name", username_box, step=2)

#     print(f"✅ Entered 'TestUser123' into Name field at ({center_x}, {center_y})")
# else:
#     print("⚠️ Name field not detected.")

# # Close WebDriver
# driver.quit()
# print("🚪 WebDriver closed.")
# # End of script

import time
import cv2
import torch
import numpy as np
import pyautogui
import pytesseract
from ultralytics import YOLO
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager

# Configure Tesseract OCR
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

# Load trained YOLO model
MODEL_PATH = r"C:\DFT\DFT\Repo\AIML\Empty Text Box(Label)\runs\detect\train2\weights\best.pt"

# Start Selenium WebDriver
chrome_options = Options()
chrome_options.add_argument("--start-maximized")
chrome_options.add_argument("--disable-blink-features=AutomationControlled")

try:
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)
except Exception as e:
    print(f"❌ Error initializing WebDriver: {e}")
    exit(1)

# Open the webpage
URL = "https://testautomationpractice.blogspot.com/"
driver.get(URL)
time.sleep(3)

# Capture screenshot
screenshot_path = "webpage.png"
driver.save_screenshot(screenshot_path)

# Load YOLO Model
try:
    model = YOLO(MODEL_PATH)
except Exception as e:
    print(f"❌ Error loading YOLO model: {e}")
    driver.quit()
    exit(1)

# Detect elements
image = cv2.imread(screenshot_path)
results = model(image)

detected_labels = {}  # Store detected labels
detected_boxes = []   # Store text boxes
debug_image = image.copy()  # Image for debugging

for result in results:
    for box in result.boxes.data:
        x1, y1, x2, y2, conf, class_id = map(int, box[:6])
        cropped_region = image[y1:y2, x1:x2]

        # Improve OCR accuracy
        detected_text = pytesseract.image_to_string(cropped_region, config='--psm 7').strip()
        detected_text_cleaned = ''.join(filter(str.isalnum, detected_text.lower()))  # Normalize text

        if class_id == 0:  # Label
            detected_labels[detected_text_cleaned] = (x1, y1, x2, y2)
            cv2.rectangle(debug_image, (x1, y1), (x2, y2), (0, 255, 0), 2)
            cv2.putText(debug_image, f"{detected_text} ({conf:.2f})", (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

        elif class_id == 1:  # Textbox
            detected_boxes.append((x1, y1, x2, y2))
            cv2.rectangle(debug_image, (x1, y1), (x2, y2), (255, 0, 0), 2)
            cv2.putText(debug_image, "Textbox", (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 0), 2)

# Save debug image
cv2.imwrite("detection_debug.png", debug_image)

# Log detected labels
print("\n🔍 Detected Labels:")
for label, bbox in detected_labels.items():
    print(f"  ➜ {label}: {bbox}")

print("\n🔍 Detected Text Boxes:")
for i, box in enumerate(detected_boxes):
    print(f"  ➜ Box {i + 1}: {box}")

# Find best match for "Name" label
username_box = None
for label, (lx1, ly1, lx2, ly2) in detected_labels.items():
    if "name" in label:  # Match normalized label
        closest_textbox = None
        min_distance = float('inf')

        for (tx1, ty1, tx2, ty2) in detected_boxes:
            distance = abs(ly2 - ty1)  # Check vertical distance
            if distance < min_distance:
                min_distance = distance
                closest_textbox = (tx1, ty1, tx2, ty2)

        username_box = closest_textbox
        break

# Function to highlight detected field
def highlight_and_capture(field_name, bbox, step):
    x1, y1, x2, y2 = bbox
    highlighted_image = image.copy()
    cv2.rectangle(highlighted_image, (x1, y1), (x2, y2), (0, 255, 255), 3)
    cv2.putText(highlighted_image, field_name, (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 255), 2)
    screenshot_filename = f"screenshot_step_{step}.png"
    cv2.imwrite(screenshot_filename, highlighted_image)
    print(f"📸 Screenshot saved: {screenshot_filename}")

# Enter text in Username field
if username_box:
    tx1, ty1, tx2, ty2 = username_box
    center_x, center_y = (tx1 + tx2) // 2, (ty1 + ty2) // 2

    highlight_and_capture("Entering Name", username_box, step=1)

    pyautogui.moveTo(center_x, center_y, duration=0.5)
    pyautogui.click()
    time.sleep(0.5)
    pyautogui.write("TestUser123", interval=0.1)

    highlight_and_capture("Entered Name", username_box, step=2)

    print(f"✅ Entered 'TestUser123' into Name field at ({center_x}, {center_y})")

    # Take a screenshot after entering data
    time.sleep(1)  # Give UI time to update
    screenshot_after_entry = "screenshot_after_entry.png"
    driver.save_screenshot(screenshot_after_entry)
    print(f"📸 Screenshot after entering data saved: {screenshot_after_entry}")

else:
    print("⚠️ Name field not detected.")

# Close WebDriver
driver.quit()
print("🚪 WebDriver closed.")
# End of script