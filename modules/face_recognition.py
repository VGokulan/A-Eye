"""
Face Recognition Module
Handles face detection, recognition, and registration using OpenCV.
"""

import cv2
import os
import time
from config import (
    FACE_OUTPUT_DIR, 
    FACE_DETECTION_SCALE_FACTOR, 
    FACE_DETECTION_MIN_NEIGHBORS, 
    FACE_DETECTION_MIN_SIZE
)
from modules.speech_manager import get_voice_input


# Create output directory if it doesn't exist
if not os.path.exists(FACE_OUTPUT_DIR):
    os.makedirs(FACE_OUTPUT_DIR)

# Load Face Detector
face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')


def get_frame():
    """
    Captures a single frame from the camera.
    
    Returns:
        numpy.ndarray: Captured frame or None if failed
    """
    try:
        cap = cv2.VideoCapture(0)  # Use default camera

        if not cap.isOpened():
            print("❌ Error: Could not open camera.")
            return None
        
        ret, frame = cap.read()
        cap.release()  # Release the camera

        if not ret:
            print("❌ Error: Failed to capture frame.")
            return None
        
        return frame
    except Exception as e:
        print(f"Error capturing frame: {e}")
        return None


def detect_faces(frame):
    """
    Detects faces in a given frame using OpenCV Haar Cascade.
    
    Args:
        frame (numpy.ndarray): Input frame to detect faces in
    
    Returns:
        list: List of face coordinates (x, y, w, h) or empty list if no faces
    """
    try:
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)  # Convert to grayscale
        faces = face_cascade.detectMultiScale(
            gray, 
            scaleFactor=FACE_DETECTION_SCALE_FACTOR, 
            minNeighbors=FACE_DETECTION_MIN_NEIGHBORS, 
            minSize=(FACE_DETECTION_MIN_SIZE, FACE_DETECTION_MIN_SIZE)
        )
        return faces
    except Exception as e:
        print(f"Error detecting faces: {e}")
        return []


def register_new_face():
    """
    Captures, detects faces, gets a name, and saves the image with the recognized name.
    
    Returns:
        str: Registered person's name or None if registration failed
    """
    try:
        print("📷 Capturing image from camera...")
        frame = get_frame()
        
        if frame is None:
            print("❌ Failed to capture image.")
            return None
        
        # Detect faces
        faces = detect_faces(frame)
        if len(faces) == 0:
            print("⚠️ No face detected! Try adjusting the camera angle or lighting.")
            return None

        # Draw rectangles around detected faces
        for (x, y, w, h) in faces:
            cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)

        # Get Name via Voice
        print("🎤 Please say your name...")
        person_name = get_voice_input()
        
        # Fallback to Manual Input
        if not person_name:
            person_name = input("Couldn't detect name. Enter manually: ").strip()
            if not person_name:
                print("❌ No name provided! Image not saved.")
                return None

        # Generate Unique File Name
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        file_name = f"{person_name}_{timestamp}.jpg"
        output_path = os.path.join(FACE_OUTPUT_DIR, file_name)

        # Save the image
        cv2.imwrite(output_path, frame)
        print(f"✅ Image saved as: {output_path}")

        # Store name in a text file (for reference)
        log_file_path = os.path.join(FACE_OUTPUT_DIR, "face_log.txt")
        with open(log_file_path, "a") as f:
            f.write(f"{person_name}, {output_path}\n")

        return person_name  # Return the detected name for further use
        
    except Exception as e:
        print(f"Error in face registration: {e}")
        return None


def recognize_registered_faces():
    """
    Attempts to recognize previously registered faces in the current frame.
    
    Returns:
        str: Recognized person's name or "Unknown" if not recognized
    """
    try:
        # Capture current frame
        frame = get_frame()
        if frame is None:
            return "Failed to capture image"
        
        # Detect faces in current frame
        faces = detect_faces(frame)
        if len(faces) == 0:
            return "No faces detected"
        
        # For now, return basic detection info
        # In a full implementation, you would compare against stored face embeddings
        return f"Detected {len(faces)} face(s)"
        
    except Exception as e:
        print(f"Error in face recognition: {e}")
        return "Recognition failed"


def get_registered_faces():
    """
    Retrieves list of all registered faces from the log file.
    
    Returns:
        list: List of registered person names
    """
    try:
        log_file_path = os.path.join(FACE_OUTPUT_DIR, "face_log.txt")
        if not os.path.exists(log_file_path):
            return []
        
        registered_faces = []
        with open(log_file_path, "r") as f:
            for line in f:
                if line.strip():
                    name = line.split(",")[0].strip()
                    if name not in registered_faces:
                        registered_faces.append(name)
        
        return registered_faces
        
    except Exception as e:
        print(f"Error reading registered faces: {e}")
        return []


def delete_face_registration(person_name):
    """
    Deletes a specific person's face registration.
    
    Args:
        person_name (str): Name of the person whose registration to delete
    
    Returns:
        bool: True if deletion successful, False otherwise
    """
    try:
        log_file_path = os.path.join(FACE_OUTPUT_DIR, "face_log.txt")
        if not os.path.exists(log_file_path):
            print(f"No registrations found for {person_name}")
            return False
        
        # Read all registrations
        registrations = []
        deleted_files = []
        
        with open(log_file_path, "r") as f:
            for line in f:
                if line.strip():
                    name, file_path = line.strip().split(",", 1)
                    if name.strip() == person_name:
                        deleted_files.append(file_path.strip())
                    else:
                        registrations.append(line)
        
        # Delete image files
        for file_path in deleted_files:
            if os.path.exists(file_path):
                os.unlink(file_path)
                print(f"Deleted image: {file_path}")
        
        # Rewrite log file without deleted registrations
        with open(log_file_path, "w") as f:
            f.writelines(registrations)
        
        print(f"Deleted {len(deleted_files)} registration(s) for {person_name}")
        return True
        
    except Exception as e:
        print(f"Error deleting face registration: {e}")
        return False


def get_face_detection_stats():
    """
    Provides statistics about face detection and registration.
    
    Returns:
        dict: Statistics about the face recognition system
    """
    try:
        stats = {
            'total_registrations': 0,
            'registered_persons': [],
            'output_directory': FACE_OUTPUT_DIR,
            'detection_parameters': {
                'scale_factor': FACE_DETECTION_SCALE_FACTOR,
                'min_neighbors': FACE_DETECTION_MIN_NEIGHBORS,
                'min_size': FACE_DETECTION_MIN_SIZE
            }
        }
        
        # Count registrations
        log_file_path = os.path.join(FACE_OUTPUT_DIR, "face_log.txt")
        if os.path.exists(log_file_path):
            with open(log_file_path, "r") as f:
                stats['total_registrations'] = len(f.readlines())
        
        # Get registered persons
        stats['registered_persons'] = get_registered_faces()
        
        return stats
        
    except Exception as e:
        print(f"Error getting face detection stats: {e}")
        return {}
