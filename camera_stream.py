import cv2
import requests
from ultralytics import YOLO

# 1. Load the YOLO model onto your laptop's local RAM memory
model = YOLO("yolov8n.pt") 

# 2. TARGET CLOUD ADDRESS (You will replace this URL after Step 5)
CLOUD_URL = "http://127.0.0"  # Defaulting to local testing first

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

    # Execute YOLO classification locally on the incoming frame
    results = model(frame)

    # Initialize tracking counts for your specific targets
    counts = {"elephant": 0, "bear": 0, "person": 0, "cow": 0, "cat": 0, "dog": 0}
    total_area = 0
    box_count = 0

    # Read through bounding box dimensions detected by YOLO
    for box in results.boxes:
        class_id = int(box.cls)
        label = model.names[class_id]
        
        if label in counts:
            counts[label] += 1
            
            # Compute box area ratio relative to full camera frame resolution
            x1, y1, x2, y2 = box.xyxy.tolist()
            box_area = (x2 - x1) * (y2 - y1)
            frame_area = frame.shape * frame.shape
            total_area += (box_area / frame_area)
            box_count += 1

    # Extract standard box size ratio parameter
    avg_box_size = (total_area / box_count) if box_count > 0 else 0.0

    # Package your data metrics into a highly optimized JSON object
    payload = {
        "elephant": counts["elephant"],
        "bear": counts["bear"],
        "person": counts["person"],
        "cow": counts["cow"],
        "cat": counts["cat"],
        "dog": counts["dog"],
        "avg_box_size": round(avg_box_size, 3)
    }

    # Only transmit data out over the internet if an animal/human is found
    if box_count > 0:
        try:
            # Post data over network to your Cloud API environment
            response = requests.post(CLOUD_URL, json=payload, timeout=2)
            if response.status_code == 200:
                print(f"📡 Cloud Sync Complete -> Verdict: {response.json()['threat_level']}")
        except requests.exceptions.RequestException:
            print("⚠️ Cloud Sync Failed: Cloud server sleeping or unreachable.")

    # Show live video window locally on your laptop
    cv2.imshow("Local YOLO Vision Processing", results.plot())
    
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()