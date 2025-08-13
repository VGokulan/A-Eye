"""
Scene Analyzer Module
Analyzes captured images to provide detailed scene descriptions using Google's Generative AI.
"""

from PIL import Image
import google.generativeai as genai
import tempfile
import cv2
import os
from config import GEMINI_API_KEY
from modules.iot_controller import get_frame, set_servo_angle

# Configure the API key for Google Generative AI
genai.configure(api_key=GEMINI_API_KEY)


def analyze_scene():
    """
    Captures and analyzes the current scene to provide a detailed description.
    
    Returns:
        str: Detailed scene description or None if analysis failed
    """
    try:
        # Set servo to optimal viewing angle
        set_servo_angle(115)
        
        # Fetch a frame from the camera
        frame = get_frame()
        
        if frame is None:
            print("Error: Could not fetch frame from camera.")
            return None
        
        # Convert BGR to RGB for PIL
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        
        # Save frame temporarily
        temp_image_path = tempfile.mktemp(suffix=".jpg")
        cv2.imwrite(temp_image_path, frame_rgb)
        
        try:
            # Load the captured image into PIL
            image = Image.open(temp_image_path)
            
            # Prompt for scene description
            prompt = "You are a describing assistant. Describe everything you see in the scene within 3 lines. Be detailed but concise."
            
            # Use the generative model to generate the description
            model = genai.GenerativeModel("gemini-1.5-flash")
            response = model.generate_content([image, prompt])
            
            # Output and return the response
            print("Scene Description:", response.text)
            return response.text
            
        finally:
            # Clean up temporary file
            if os.path.exists(temp_image_path):
                os.unlink(temp_image_path)
                
    except Exception as e:
        print(f"An error occurred while analyzing scene: {e}")
        return None


def analyze_specific_object(object_description):
    """
    Analyzes a specific object or area in the scene based on user description.
    
    Args:
        object_description (str): Description of what to focus on in the scene
    
    Returns:
        str: Analysis of the specified object or area
    """
    try:
        # Set servo to optimal viewing angle
        set_servo_angle(115)
        
        # Fetch a frame from the camera
        frame = get_frame()
        
        if frame is None:
            print("Error: Could not fetch frame from camera.")
            return None
        
        # Convert BGR to RGB for PIL
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        
        # Save frame temporarily
        temp_image_path = tempfile.mktemp(suffix=".jpg")
        cv2.imwrite(temp_image_path, frame_rgb)
        
        try:
            # Load the captured image into PIL
            image = Image.open(temp_image_path)
            
            # Prompt for specific object analysis
            prompt = f"Focus on the following object/area: {object_description}. Describe what you see in detail within 3 lines."
            
            # Use the generative model to generate the description
            model = genai.GenerativeModel("gemini-1.5-flash")
            response = model.generate_content([image, prompt])
            
            # Output and return the response
            print("Object Analysis:", response.text)
            return response.text
            
        finally:
            # Clean up temporary file
            if os.path.exists(temp_image_path):
                os.unlink(temp_image_path)
                
    except Exception as e:
        print(f"An error occurred while analyzing object: {e}")
        return None


def get_scene_summary():
    """
    Provides a brief summary of the current scene.
    
    Returns:
        str: Brief scene summary or None if failed
    """
    try:
        # Set servo to optimal viewing angle
        set_servo_angle(115)
        
        # Fetch a frame from the camera
        frame = get_frame()
        
        if frame is None:
            print("Error: Could not fetch frame from camera.")
            return None
        
        # Convert BGR to RGB for PIL
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        
        # Save frame temporarily
        temp_image_path = tempfile.mktemp(suffix=".jpg")
        cv2.imwrite(temp_image_path, frame_rgb)
        
        try:
            # Load the captured image into PIL
            image = Image.open(temp_image_path)
            
            # Prompt for scene summary
            prompt = "Provide a brief, one-line summary of what you see in this scene."
            
            # Use the generative model to generate the summary
            model = genai.GenerativeModel("gemini-1.5-flash")
            response = model.generate_content([image, prompt])
            
            # Output and return the response
            print("Scene Summary:", response.text)
            return response.text
            
        finally:
            # Clean up temporary file
            if os.path.exists(temp_image_path):
                os.unlink(temp_image_path)
                
    except Exception as e:
        print(f"An error occurred while generating scene summary: {e}")
        return None
