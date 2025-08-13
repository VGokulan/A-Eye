"""
Navigation Assistant Module
Provides navigation guidance and object location information using computer vision.
"""

import PIL
import google.generativeai as genai
import cv2
import tempfile
import os
from PIL import Image
from config import GEMINI_API_KEY
from modules.iot_controller import get_frame, set_servo_angle
from modules.speech_manager import speak_text, get_voice_input

# Configure the API key for Google Generative AI
genai.configure(api_key=GEMINI_API_KEY)


def analyze_environment():
    """
    Analyzes the current environment to identify objects that can serve as navigation destinations.
    
    Returns:
        str: List of objects and their locations in the environment
    """
    try:
        # Set servo to optimal viewing angle
        set_servo_angle(90)
        
        # Fetch a frame from the camera
        frame = get_frame()
        
        if frame is None:
            print("Error: Could not fetch frame from camera.")
            return None
        
        # Convert BGR to RGB for PIL
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        
        # Save the captured frame temporarily as an image
        temp_image_path = tempfile.mktemp(suffix=".jpg")
        cv2.imwrite(temp_image_path, frame_rgb)
        
        try:
            # Load the captured image into PIL
            image = Image.open(temp_image_path)
            
            # Prompt for environment analysis
            prompt = """You are a describing agent whose purpose is to give me objects in an environment 
            which I will use as destinations. Just list me a set of objects and describe where they are. 
            Do not use special symbols in the output."""
            
            # Use the generative model to generate the description
            model = genai.GenerativeModel("gemini-1.5-flash")
            response = model.generate_content([image, prompt])
            
            # Output and return the response
            print("Environment Analysis:", response.text)
            speak_text(response.text)
            return response.text
            
        finally:
            # Clean up temporary file
            if os.path.exists(temp_image_path):
                os.unlink(temp_image_path)
                
    except Exception as e:
        print(f"An error occurred while analyzing environment: {e}")
        return None


def provide_navigation_guidance(destination):
    """
    Provides navigation guidance to a specific destination in the current environment.
    
    Args:
        destination (str): Description of the destination object or location
    
    Returns:
        str: Navigation guidance instructions
    """
    try:
        # Set servo to optimal viewing angle
        set_servo_angle(90)
        
        # Fetch a frame from the camera
        frame = get_frame()
        
        if frame is None:
            print("Error: Could not fetch frame from camera.")
            return None
        
        # Convert BGR to RGB for PIL
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        
        # Save the captured frame temporarily as an image
        temp_image_path = tempfile.mktemp(suffix=".jpg")
        cv2.imwrite(temp_image_path, frame_rgb)
        
        try:
            # Load the captured image into PIL
            image = Image.open(temp_image_path)
            
            # Prompt for navigation guidance
            prompt = f"""You are a navigation assistant. You are going to guide me to my destination. 
            Make sure to be precise, assume that the image is what I am facing. 
            Destination: {destination}"""
            
            # Use the generative model to generate the guidance
            model = genai.GenerativeModel("gemini-1.5-flash")
            response = model.generate_content([image, prompt])
            
            # Output and return the response
            print("Navigation Guidance:", response.text)
            speak_text(response.text)
            return response.text
            
        finally:
            # Clean up temporary file
            if os.path.exists(temp_image_path):
                os.unlink(temp_image_path)
                
    except Exception as e:
        print(f"An error occurred while providing navigation guidance: {e}")
        return None


def interactive_navigation():
    """
    Interactive navigation session that allows users to select destinations and get guidance.
    
    Returns:
        str: Final navigation result or None if failed
    """
    try:
        # First, analyze the environment
        environment_info = analyze_environment()
        if not environment_info:
            return None
        
        # Ask user to select a destination
        speak_text("Select an object to mark as destination")
        destination = get_voice_input()
        
        if not destination:
            print("No destination selected.")
            return None
        
        # Provide navigation guidance
        guidance = provide_navigation_guidance(destination)
        return guidance
        
    except Exception as e:
        print(f"Error in interactive navigation: {e}")
        return None


def get_route_alternatives(destination):
    """
    Provides alternative routes or approaches to reach a destination.
    
    Args:
        destination (str): Description of the destination
    
    Returns:
        str: Alternative route suggestions
    """
    try:
        # Set servo to optimal viewing angle
        set_servo_angle(90)
        
        # Fetch a frame from the camera
        frame = get_frame()
        
        if frame is None:
            print("Error: Could not fetch frame from camera.")
            return None
        
        # Convert BGR to RGB for PIL
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        
        # Save the captured frame temporarily as an image
        temp_image_path = tempfile.mktemp(suffix=".jpg")
        cv2.imwrite(temp_image_path, frame_rgb)
        
        try:
            # Load the captured image into PIL
            image = Image.open(temp_image_path)
            
            # Prompt for alternative routes
            prompt = f"""You are a navigation assistant. For the destination '{destination}', 
            provide 2-3 alternative approaches or routes to reach it. 
            Consider different angles, paths, or methods. Be specific and actionable."""
            
            # Use the generative model to generate the alternatives
            model = genai.GenerativeModel("gemini-1.5-flash")
            response = model.generate_content([image, prompt])
            
            # Output and return the response
            print("Alternative Routes:", response.text)
            speak_text(response.text)
            return response.text
            
        finally:
            # Clean up temporary file
            if os.path.exists(temp_image_path):
                os.unlink(temp_image_path)
                
    except Exception as e:
        print(f"An error occurred while getting route alternatives: {e}")
        return None


def estimate_distance_to_destination(destination):
    """
    Estimates the approximate distance to a destination based on visual analysis.
    
    Args:
        destination (str): Description of the destination
    
    Returns:
        str: Distance estimation and approach guidance
    """
    try:
        # Set servo to optimal viewing angle
        set_servo_angle(90)
        
        # Fetch a frame from the camera
        frame = get_frame()
        
        if frame is None:
            print("Error: Could not fetch frame from camera.")
            return None
        
        # Convert BGR to RGB for PIL
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        
        # Save the captured frame temporarily as an image
        temp_image_path = tempfile.mktemp(suffix=".jpg")
        cv2.imwrite(temp_image_path, frame_rgb)
        
        try:
            # Load the captured image into PIL
            image = Image.open(temp_image_path)
            
            # Prompt for distance estimation
            prompt = f"""You are a navigation assistant. For the destination '{destination}', 
            estimate the approximate distance and provide guidance on how to approach it. 
            Use relative terms like 'close', 'medium distance', 'far' and give specific movement instructions."""
            
            # Use the generative model to generate the estimation
            model = genai.GenerativeModel("gemini-1.5-flash")
            response = model.generate_content([image, prompt])
            
            # Output and return the response
            print("Distance Estimation:", response.text)
            speak_text(response.text)
            return response.text
            
        finally:
            # Clean up temporary file
            if os.path.exists(temp_image_path):
                os.unlink(temp_image_path)
                
    except Exception as e:
        print(f"An error occurred while estimating distance: {e}")
        return None
