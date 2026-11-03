import cv2
import requests
from ultralytics import YOLO

# 1. Load the YOLO model onto your laptop's local RAM memory
model = YOLO("yolov8n.pt") 

# 2. TARGET CLOUD ADDRESS (Replace this with your exact live link from Render!)
CLOUD_URL = "https://onrender.com" 

# Strict COCO Dataset mapping to fix false identifications and ignore junk (like teddy bears)
TARGET_CLASSES = {
    20: "elephant",
    21: "bear",
    0: "person",
    19: "cow",
    15: "cat",
    16: "dog"
}

HIGH_LEVEL_THREATS = ["elephant", "bear"]
LOW_LEVEL_THREATS = ["person", "cow", "cat", "dog"]

# 3. Connect to your laptop's built-in webcam stream
cap = cv2.VideoCapture(0)

if not cap.isOpened():
    print("❌ Error: Cannot open the webcam stream.")
    exit()

print("🚀 Local Camera AI Tracking System Active. Press 'q' to stop.")

while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        print("❌ Dropped frame caught.")
        break

    # Run YOLO with a strict 50% confidence floor to wipe out false targets
    results = model.predict(frame, conf=0.50, verbose=False)

    # Initialize tracking counts for your specific targets
    counts = {"elephant": 0, "bear": 0, "person": 0, "cow": 0, "cat": 0, "dog": 0}
    total_area = 0
    box_count = 0
    current_highest_threat = "NO THREAT"

    # CRUCIAL FIX FOR LINE 51: Extract the first frame result from the results list
    if len(results) > 0:
        frame_result = results[0]  # <--- Wipes out the AttributeError!

        # Read through bounding box dimensions detected by YOLO
        if frame_result.boxes is not None:
            for box in frame_result.boxes:
                class_id = int(box.cls[0])  # Extract class ID safely
                
                # FILTER: Only process the box if it belongs strictly to our target list
                if class_id in TARGET_CLASSES:
                    label = TARGET_CLASSES[class_id]
                    counts[label] += 1
                    
                    # Categorize the threat level locally for your console logs
                    if label in HIGH_LEVEL_THREATS:
                        current_highest_threat = "🚨 CRITICAL HIGH-LEVEL THREAT"
                    elif label in LOW_LEVEL_THREATS and current_highest_threat != "🚨 CRITICAL HIGH-LEVEL THREAT":
                        current_highest_threat = "🟢 LOW-LEVEL THREAT DETECTED"
                    
                    # Compute box area ratio relative to full camera frame resolution safely
                    x1, y1, x2, y2 = box.xyxy[0].tolist()
                    box_area = (x2 - x1) * (y2 - y1)
                    frame_area = frame.shape[0] * frame.shape[1]
                    total_area += (box_area / frame_area)
                    box_count += 1

    # Zero-Division Guard Check
    avg_box_size = round((total_area / box_count), 3) if box_count > 0 else 0.0

    # Package data metrics into a highly optimized JSON object
    payload = {
        "elephant": counts["elephant"],
        "bear": counts["bear"],
        "person": counts["person"],
        "cow": counts["cow"],
        "cat": counts["cat"],
        "dog": counts["dog"],
        "avg_box_size": avg_box_size
    }

    # Only transmit data if a target animal or human is actively found
    if box_count > 0:
        print(f"👁️ Status -> {current_highest_threat} | Elephants: {counts['elephant']} | Bears: {counts['bear']}")
        try:
            # Post data over network to your Cloud API environment
            response = requests.post(CLOUD_URL, json=payload, timeout=2)
            if response.status_code == 200:
                print(f"📡 Cloud Sync Complete -> Verdict: {response.json()['threat_level']}")
        except requests.exceptions.RequestException:
            print("⚠️ Cloud Sync Failed: Cloud server sleeping or unreachable.")

    # Show live video window locally on your laptop
    if len(results) > 0:
        cv2.imshow("Local YOLO Vision Processing", results[0].plot())
    else:
        cv2.imshow("Local YOLO Vision Processing", frame)
    
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()