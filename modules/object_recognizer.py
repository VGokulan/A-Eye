"""
Object Recognition Module
Identifies objects in images and provides information about where to purchase them.
"""

import google.generativeai as genai
import cv2
import tempfile
import os
from config import GEMINI_API_KEY
from modules.iot_controller import get_frame
from modules.speech_manager import speak_text
from PIL import Image

# Configure the API key for Google Generative AI
genai.configure(api_key=GEMINI_API_KEY)


def recognize_object():
    """
    Captures an image and identifies the object being held, providing purchase information.
    
    Returns:
        str: Object description and purchase information or None if recognition failed
    """
    try:
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
            
            # Prompt for object recognition and purchase information
            prompt = """Tell me about the object I am holding. What is this? 
            Provide both online and offline purchase suggestions. 
            Describe as much as possible within 3 lines. 
            Do not use special symbols like (#, *, etc)."""
            
            # Use the generative model to generate the response
            model = genai.GenerativeModel("gemini-1.5-flash")
            response = model.generate_content([image, prompt])
            
            # Output and return the response
            context = response.text
            print("Object Recognition:", context)
            speak_text(context)
            return context
            
        finally:
            # Clean up temporary file
            if os.path.exists(temp_image_path):
                os.unlink(temp_image_path)
                
    except Exception as e:
        print(f"An error occurred while recognizing object: {e}")
        return None


def generate_contextual_response(user_input, context):
    """
    Generates a response based on the previous object recognition context.
    
    Args:
        user_input (str): User's follow-up question
        context (str): Previous object recognition context
    
    Returns:
        str: Generated response or error message
    """
    if context:
        try:
            model = genai.GenerativeModel("gemini-1.5-flash")
            combined_input = context + "\n" + "User: " + user_input
            response = model.generate_content([combined_input])
            print("Contextual Response:", response.text)
            return response.text
        except Exception as e:
            print(f"Error generating contextual response: {e}")
            return "Sorry, I couldn't process your request."
    else:
        return "There is no context available to respond to your question."


def handle_follow_up_queries(context):
    """
    Handles follow-up questions from the user based on object recognition context.
    
    Args:
        context (str): Previous object recognition context
    """
    from modules.speech_manager import get_voice_input
    
    while True:
        speak_text("You can ask follow-up questions or say 'exit' to end.")
        user_query = get_voice_input()

        if user_query:
            user_query = user_query.lower()
            if "exit" in user_query:
                speak_text("Exiting follow-up session.")
                print("Exiting follow-up session.")
                break
            else:
                print("Answering based on previous context...")
                response = generate_contextual_response(user_query, context)
                speak_text(response)
        else:
            speak_text("No valid input detected. Please try again or say 'exit' to end.")
            print("Invalid input for follow-up. Waiting for valid input...")


def analyze_multiple_objects():
    """
    Analyzes multiple objects in the scene and provides information about each.
    
    Returns:
        str: Analysis of multiple objects or None if failed
    """
    try:
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
            
            # Prompt for multiple object analysis
            prompt = """Identify and describe all visible objects in this scene. 
            For each object, provide a brief description and where it might be available for purchase. 
            Keep the total response within 5 lines."""
            
            # Use the generative model to generate the response
            model = genai.GenerativeModel("gemini-1.5-flash")
            response = model.generate_content([image, prompt])
            
            # Output and return the response
            result = response.text
            print("Multiple Objects Analysis:", result)
            speak_text(result)
            return result
            
        finally:
            # Clean up temporary file
            if os.path.exists(temp_image_path):
                os.unlink(temp_image_path)
                
    except Exception as e:
        print(f"An error occurred while analyzing multiple objects: {e}")
        return None
