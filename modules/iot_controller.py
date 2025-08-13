"""
IoT Controller Module
Handles camera operations and servo motor control for the AEye system.
"""

import cv2
import urllib.request
import numpy as np
import requests
from config import ESP32_CAM_URL, ESP32_SERVO_URL, CAMERA_INDEX


def get_frame():
    """
    Fetches a single frame from the camera (ESP32-CAM or local webcam).
    
    Returns:
        numpy.ndarray: Captured frame as OpenCV image array or None if failed
    """
    try:
        # Try ESP32-CAM first
        img_resp = urllib.request.urlopen(ESP32_CAM_URL, timeout=5)
        imgnp = np.array(bytearray(img_resp.read()), dtype=np.uint8)
        frame = cv2.imdecode(imgnp, -1)  # Decode image
        
        if frame is not None:
            return frame
    except Exception as e:
        print(f"ESP32-CAM not available, using local camera: {e}")
    
    try:
        # Fallback to local webcam
        cap = cv2.VideoCapture(CAMERA_INDEX)
        if not cap.isOpened():
            print("Error: Could not open local camera.")
            return None
        
        ret, frame = cap.read()
        cap.release()  # Release the capture device
        
        if not ret:
            print("Error: Failed to capture frame from local camera.")
            return None
        
        return frame
    except Exception as e:
        print(f"Error accessing local camera: {e}")
        return None


def set_servo_angle(angle):
    """
    Sends a request to the ESP32 to set the servo angle.
    
    Args:
        angle (int): Servo angle in degrees (0-180)
    
    Returns:
        bool: True if servo control successful, False otherwise
    """
    try:
        url = f"{ESP32_SERVO_URL}/servo_angle?value={angle}"
        response = requests.get(url, timeout=5)
        
        if response.status_code == 200:
            print(f"Servo moved to angle {angle}°")
            return True
        else:
            print(f"Failed to move servo to angle {angle}°. HTTP Status Code: {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"Error controlling servo: {e}")
        return False
    except Exception as e:
        print(f"Unexpected error in servo control: {e}")
        return False


def get_camera_status():
    """
    Checks the status of both ESP32-CAM and local camera.
    
    Returns:
        dict: Status information for both cameras
    """
    status = {
        'esp32_cam': False,
        'local_camera': False,
        'esp32_cam_url': ESP32_CAM_URL,
        'local_camera_index': CAMERA_INDEX
    }
    
    # Check ESP32-CAM
    try:
        response = requests.get(ESP32_CAM_URL, timeout=3)
        status['esp32_cam'] = response.status_code == 200
    except:
        status['esp32_cam'] = False
    
    # Check local camera
    try:
        cap = cv2.VideoCapture(CAMERA_INDEX)
        status['local_camera'] = cap.isOpened()
        cap.release()
    except:
        status['local_camera'] = False
    
    return status
