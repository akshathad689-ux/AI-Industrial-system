import cv2
import requests
import time
from datetime import datetime
import random

# ---------------- TELEGRAM ----------------
BOT_TOKEN = "YOUR_TELEGRAM_BOT_TOKEN"
CHAT_ID = "YOUR_CHAT_ID"

def send_alert(message):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    data = {"chat_id": CHAT_ID, "text": message}
    requests.post(url, data=data)

# ---------------- CAMERA + AI ----------------
hog = cv2.HOGDescriptor()
hog.setSVMDetector(cv2.HOGDescriptor_getDefaultPeopleDetector())

cap = cv2.VideoCapture(0)

last_alert_time = 0

while True:
    ret, frame = cap.read()
    if not ret:
        break

    boxes, _ = hog.detectMultiScale(frame)

    human_detected = len(boxes) > 0

    frame_width = frame.shape[1]

    zone = "NO HUMAN"
    distance = "FAR"
    gas_status = "SAFE"

    # ---------------- SIMULATED GAS SENSOR ----------------
    gas_level = random.randint(0, 100)

    if gas_level > 60:
        gas_status = "GAS PRESENT"
    else:
        gas_status = "SAFE"

    for (x, y, w, h) in boxes:

        # -------- ZONE MAPPING --------
        center_x = x + w // 2

        if center_x < frame_width / 3:
            zone = "ZONE A"
        elif center_x < 2 * frame_width / 3:
            zone = "ZONE B"
        else:
            zone = "ZONE C"

        # -------- DISTANCE --------
        if w > 150:
            distance = "NEAR"
            color = (0, 0, 255)
        else:
            distance = "FAR"
            color = (0, 255, 0)

        cv2.rectangle(frame, (x, y), (x+w, y+h), color, 2)

    # ---------------- TIME ----------------
    current_time = datetime.now().strftime("%H:%M:%S")

    # ---------------- DISPLAY ----------------
    cv2.putText(frame, f"Human: {human_detected}", (10, 30),
                cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255,255,255), 2)

    cv2.putText(frame, f"Zone: {zone}", (10, 60),
                cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255,255,255), 2)

    cv2.putText(frame, f"Distance: {distance}", (10, 90),
                cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255,255,255), 2)

    cv2.putText(frame, f"Gas: {gas_status}", (10, 120),
                cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255,255,255), 2)

    cv2.putText(frame, f"Time: {current_time}", (10, 150),
                cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255,255,255), 2)

    # ---------------- ALERT LOGIC ----------------
    danger_level = "SAFE"

    if human_detected and gas_status == "GAS PRESENT":
        if distance == "NEAR":
            danger_level = "CRITICAL"
        else:
            danger_level = "ALERT"
    elif human_detected:
        danger_level = "MONITOR"
    elif gas_status == "GAS PRESENT":
        danger_level = "WARNING"

    # ---------------- TELEGRAM ALERT ----------------
    if danger_level != "SAFE":
        if time.time() - last_alert_time > 10:

            message = f"""
🚨 INDUSTRIAL ALERT SYSTEM 🚨

Time: {current_time}
Human: {human_detected}
Zone: {zone}
Distance: {distance}
Gas Status: {gas_status}
Danger Level: {danger_level}
"""

            print(message)
            send_alert(message)
            last_alert_time = time.time()

    cv2.imshow("Industrial AI Safety System", frame)

    if cv2.waitKey(1) == 27:
        break

cap.release()
cv2.destroyAllWindows()