import os
import sys
import time
import math

# Redirect stdout to null temporarily to suppress YOLO loading messages
sys.stdout = open(os.devnull, "w")

import cv2
import numpy as np
from ultralytics import YOLO
import RPi.GPIO as GPIO
from picamera2 import Picamera2

# Restore stdout
sys.stdout = sys.__stdout__

# Configure servo GPIO
servo_pin = 18  # GPIO pin for servo control
GPIO.setmode(GPIO.BCM)
GPIO.setup(servo_pin, GPIO.OUT)
servo_pwm = GPIO.PWM(servo_pin, 50)  # 50 Hz frequency
servo_pwm.start(0)  # Initialize with 0% duty cycle

# Load YOLO model
model = YOLO("Models/yolov5n.pt")

# Detection sensitivity
sensitivity = 300

def clamp(n, min_val, max_val):
    """Clamp a value between min and max."""
    return max(min(n, max_val), min_val)

def set_servo_angle(angle):
    """
    Set servo angle between 0 and 180 degrees.
    Converts angle to duty cycle and sets the servo position.
    """
    # Convert angle to duty cycle (typically 2.5% to 12.5% for 0-180 degrees)
    duty_cycle = 2.5 + (angle / 180) * 10
    servo_pwm.ChangeDutyCycle(duty_cycle)
    time.sleep(0.01)  # Short delay to allow servo to move

def setup_camera():
    """Initialize Raspberry Pi camera"""
    picam2 = Picamera2()
    config = picam2.create_preview_configuration(main={"size": (640, 480)})
    picam2.configure(config)
    picam2.start()
    time.sleep(1)  # Give camera time to warm up
    return picam2

try:
    # Initialize camera
    camera = setup_camera()
    
    # Get first frame for optical flow
    prev_frame = camera.capture_array()
    prev_gray = cv2.cvtColor(prev_frame, cv2.COLOR_BGR2GRAY)
    
    frame_number = 0
    
    # Main loop
    while True:
        # Capture frame
        frame = camera.capture_array()
        frame_number += 1
        
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
                            masked_magnitude = cv2.bitwise_and(
                                magnitude, magnitude, mask=mask
                            )
                            mean_flow = (
                                (masked_magnitude.mean() / pow(x2 - x1, 2))
                                * 4000
                                * 1000
                            )
                            print(f"Mean flow: {mean_flow}")
                            
                            if mean_flow > sensitivity:
                                # Calculate servo angle (0-180 degrees) based on person position
                                # Original calculation was: clamp((((x1 + x2) / 2) - 140) * 0.3, 0, 140)
                                # Modified for servo angle range (0-180)
                                center_x = (x1 + x2) / 2
                                frame_width = frame.shape[1]
                                # Map center position (0 to frame_width) to servo angle (0 to 180)
                                servo_angle = clamp(180 * (center_x / frame_width), 0, 180)
                                
                                print(f"Person detected at position: {center_x}, setting servo angle: {servo_angle}")
                                set_servo_angle(servo_angle)
        
        prev_gray = gray
        
        # Display the frame with detections
        frame_with_detections = results[0].plot()
        cv2.imshow("Frame", frame_with_detections)
        
        if cv2.waitKey(25) & 0xFF == ord("q"):
            break

except KeyboardInterrupt:
    print("Program stopped by user")
finally:
    # Clean up
    cv2.destroyAllWindows()
    servo_pwm.stop()
    GPIO.cleanup()
    print("Resources released")