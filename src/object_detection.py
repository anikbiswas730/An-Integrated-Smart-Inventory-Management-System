# src/object_detection.py
import torch
import cv2
import pandas as pd
import serial
import time

# Load YOLOv5 model (small variant)
model = torch.hub.load('ultralytics/yolov5', 'yolov5s', pretrained=True)
model.conf = 0.45  # Confidence threshold

# Serial to Arduino
arduino = serial.Serial('/dev/ttyACM0', 115200, timeout=1)
time.sleep(2)  # Wait for Arduino reset

def detect_target_object(frame, target_class):
    results = model(frame)
    df = results.pandas().xyxy[0]

    for _, row in df.iterrows():
        class_name = row['name']
        confidence = row['confidence']
        if class_name == target_class and confidence >= 0.45:
            xc = (row['xmin'] + row['xmax']) / 2
            yc = (row['ymin'] + row['ymax']) / 2
            print(f"[DETECT] Found {target_class} at ({xc:.1f}, {yc:.1f})")
            arduino.write(b'gotit\n')
            return True, results.render()[0]
    return False, frame

if __name__ == "__main__":
    cap = cv2.VideoCapture(0)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 320)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 240)

    target = "bottle"  # Example
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        found, out_frame = detect_target_object(frame, target)
        cv2.imshow("Detection", out_frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    cap.release()
    cv2.destroyAllWindows()
