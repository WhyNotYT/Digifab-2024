import os
import sys
import serial
import time

sys.stdout = open(os.devnull, "w")

import cv2
import numpy as np
from ultralytics import YOLO

sys.stdout = sys.__stdout__


ser = serial.Serial("COM3", 115200)

model = YOLO("Models/yolov5n.pt")

sys.stdout = sys.__stdout__

sensitivity = 0.25

cap = cv2.VideoCapture(0)
ret, prev_frame = cap.read()
prev_gray = cv2.cvtColor(prev_frame, cv2.COLOR_BGR2GRAY)

frame_number = 0

while True:
    ret, frame = cap.read()
    frame_number += 1

    if ret:
        # Convert current frame to grayscale
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        # Calculate optical flow using Lucas-Kanade method
        lk_params = dict(
            winSize=(15, 15),
            maxLevel=2,
            criteria=(cv2.TERM_CRITERIA_EPS | cv2.TERM_CRITERIA_COUNT, 10, 0.03),
        )
        flow = cv2.calcOpticalFlowFarneback(
            prev_gray, gray, None, 0.5, 3, 15, 3, 5, 1.2, 0
        )

        # Calculate the magnitude and angle of the optical flow vectors
        magnitude, angle = cv2.cartToPolar(flow[..., 0], flow[..., 1])

        # Create a mask to compute the mean flow within the bounding box of each person detected
        mask = np.zeros_like(gray)

        # Detect objects and track persons
        results = model.track(frame, persist=True)

        for result in results:
            if hasattr(result, "boxes"):
                for box in result.boxes.xyxy:
                    x1, y1, x2, y2 = map(int, box[:4])
                    cls = 0
                    if cls in result.names:
                        label = result.names[cls]
                        if label == "person":
                            mask[y1:y2, x1:x2] = 255

        # Compute the mean flow within the masked area
        masked_magnitude = cv2.bitwise_and(magnitude, magnitude, mask=mask)
        mean_flow = masked_magnitude.mean()
        print(mean_flow)
        # Display flow vectors in a separate window
        hsv = np.zeros_like(frame)
        hsv[..., 1] = 255
        hsv[..., 0] = angle * 180 / np.pi / 2
        hsv[..., 2] = cv2.normalize(masked_magnitude, None, 0, 255, cv2.NORM_MINMAX)
        flow_image = cv2.cvtColor(hsv, cv2.COLOR_HSV2BGR)
        cv2.imshow("Flow Vectors", flow_image)

        if mean_flow > sensitivity:
            print("Person moved in frame:", frame_number)
            ser.write(b"on\n")

        prev_gray = gray

        frame_ = results[0].plot()

        cv2.imshow("Frame", frame_)

        if cv2.waitKey(25) & 0xFF == ord("q"):
            break

cap.release()
cv2.destroyAllWindows()
