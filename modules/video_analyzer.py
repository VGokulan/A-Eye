"""
Video Analyzer Module
Handles video frame capture, face recognition, and scene description generation.
"""

import os
import time
from threading import Thread
from queue import Queue
from moviepy.video.io.VideoFileClip import VideoFileClip
import google.generativeai as genai
from fpdf import FPDF
import re
from PIL import Image
import cv2
import json
from datetime import datetime
import face_recognition
from config import GEMINI_API_KEY

# Configure Google Generative AI
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel("gemini-1.5-flash")


def replace_special_characters(text):
    """
    Replace special characters with their ASCII equivalents.

    Args:
        text (str): Input text with special characters

    Returns:
        str: Text with replaced special characters
    """
    text = text.replace("'", "'").replace("'", "'")
    text = text.replace(""", '"').replace(""", '"')
    text = text.replace("–", "-").replace("—", "-")
    text = text.replace("•", "*")
    return text


def load_known_faces(known_faces_dir):
    """
    Load known face encodings and names from a directory.

    Args:
        known_faces_dir (str): Directory containing known face images

    Returns:
        tuple: (known_encodings, known_names)
    """
    try:
        known_encodings = []
        known_names = []
        
        if not os.path.exists(known_faces_dir):
            print(f"Warning: Known faces directory {known_faces_dir} does not exist")
            return known_encodings, known_names
            
        for filename in os.listdir(known_faces_dir):
            if filename.lower().endswith((".png", ".jpg", ".jpeg")):
                image_path = os.path.join(known_faces_dir, filename)
                image = face_recognition.load_image_file(image_path)
                encodings = face_recognition.face_encodings(image)
                if encodings:
                    known_encodings.append(encodings[0])
                    known_names.append(os.path.splitext(filename)[0])
        
        return known_encodings, known_names
    except Exception as e:
        print(f"Error loading known faces: {e}")
        return [], []


def recognize_faces(image_path, known_encodings, known_names):
    """
    Recognize faces in an image using known face encodings.

    Args:
        image_path (str): Path to the image to analyze
        known_encodings (list): List of known face encodings
        known_names (list): List of known face names

    Returns:
        list: List of recognized face names
    """
    try:
        image = face_recognition.load_image_file(image_path)
        encodings = face_recognition.face_encodings(image)
        recognized_faces = []
        
        for encoding in encodings:
            if known_encodings:
                results = face_recognition.compare_faces(known_encodings, encoding)
                distances = face_recognition.face_distance(known_encodings, encoding)
                if any(results):
                    best_match_index = distances.argmin()
                    recognized_faces.append(known_names[best_match_index])
                else:
                    recognized_faces.append("Unknown")
            else:
                recognized_faces.append("Unknown")
        
        return recognized_faces
    except Exception as e:
        print(f"Error recognizing faces: {e}")
        return []


def capture_frames(output_folder, frame_queue, interval):
    """
    Capture frames from camera at specified intervals.

    Args:
        output_folder (str): Directory to save captured frames
        frame_queue (Queue): Queue to store captured frame data
        interval (int): Interval in seconds between frame captures
    """
    try:
        if not os.path.exists(output_folder):
            os.makedirs(output_folder)

        cap = cv2.VideoCapture(0)
        if not cap.isOpened():
            print("Error: Could not access the camera.")
            return

        frame_count = 0
        fps = cap.get(cv2.CAP_PROP_FPS) or 30
        frame_interval = int(fps * interval)

        print("Starting camera feed. Press 'q' to stop.")
        while True:
            ret, frame = cap.read()
            if not ret:
                print("Error: Could not read from camera.")
                break

            if frame_count % frame_interval == 0:
                timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                frame_filename = os.path.join(output_folder, f"frame_{frame_count}.jpg")
                cv2.imwrite(frame_filename, frame)
                frame_queue.put((frame_filename, timestamp))
                print(f"Captured frame: {frame_filename}")

            frame_count += 1
            cv2.imshow("Camera Feed", frame)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

        cap.release()
        cv2.destroyAllWindows()
        frame_queue.put(None)  # Signal the end of capturing
        print("Stopped capturing frames.")
        
    except Exception as e:
        print(f"Error in frame capture: {e}")


def describe_frames(frame_queue, pdf_path, known_encodings, known_names):
    """
    Generate descriptions for captured frames and save to PDF.

    Args:
        frame_queue (Queue): Queue containing captured frame data
        pdf_path (str): Path to save the output PDF
        known_encodings (list): List of known face encodings
        known_names (list): List of known face names
    """
    try:
        pdf = FPDF()
        
        while True:
            frame_data = frame_queue.get()
            if frame_data is None:  # End signal
                break

            frame_path, timestamp = frame_data
            print(f"Processing frame: {frame_path}")
            
            # Recognize faces in the frame
            recognized_faces = recognize_faces(frame_path, known_encodings, known_names)
            faces_text = ", ".join(recognized_faces) if recognized_faces else "No faces recognized"

            # Prepare the prompt
            prompt = (
                f"You are describing a video frame to a blind person. Be as vivid and detailed as possible.\n"
                f"- Timestamp: {timestamp}\n"
                f"- Recognized Faces: {faces_text}\n\n"
                f"Describe the scene in detail."
            )

            try:
                # Open the image using PIL
                image = Image.open(frame_path)

                # Pass the text and image to the generative model
                response = model.generate_content([prompt, image])

                # Process the API response
                description_text = replace_special_characters(response.text)
            except Exception as e:
                print(f"Error generating description: {e}")
                description_text = "Error generating description."

            # Add the description to the PDF
            pdf.add_page()
            pdf.set_font("Arial", size=12)
            pdf.multi_cell(0, 10, description_text)

        # Save the PDF
        pdf.output(pdf_path)
        print(f"Descriptions saved to PDF: {pdf_path}")
        
    except Exception as e:
        print(f"Error in frame description: {e}")


def start_video_analysis(output_folder="frames", output_pdf="descriptions.pdf", 
                        interval=6, known_faces_dir=None):
    """
    Start the video analysis process with frame capture and description generation.

    Args:
        output_folder (str): Directory to save captured frames
        output_pdf (str): Path to save the output PDF
        interval (int): Interval in seconds between frame captures
        known_faces_dir (str): Directory containing known face images
    """
    try:
        # Set up threading
        frame_queue = Queue()
        
        # Load known faces if directory is provided
        known_encodings, known_names = [], []
        if known_faces_dir and os.path.exists(known_faces_dir):
            known_encodings, known_names = load_known_faces(known_faces_dir)

        # Create and start threads
        capture_thread = Thread(target=capture_frames, args=(output_folder, frame_queue, interval))
        describe_thread = Thread(target=describe_frames, args=(frame_queue, output_pdf, known_encodings, known_names))

        # Start threads
        capture_thread.start()
        describe_thread.start()

        # Wait for threads to complete
        capture_thread.join()
        describe_thread.join()

        print("Frame capturing and description completed.")
        
    except Exception as e:
        print(f"Error starting video analysis: {e}")


def get_video_analysis_stats():
    """
    Get statistics about the video analysis system.

    Returns:
        dict: Statistics about the video analysis system
    """
    try:
        stats = {
            'output_folders': [],
            'known_faces_loaded': 0,
            'model_configured': bool(GEMINI_API_KEY)
        }
        
        # Check for output folders
        if os.path.exists("frames"):
            stats['output_folders'].append("frames")
            
        return stats
        
    except Exception as e:
        print(f"Error getting video analysis stats: {e}")
        return {}
