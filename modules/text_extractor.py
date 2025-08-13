"""
Text Extraction Module
Extracts text from images using OCR (Optical Character Recognition) technology.
"""

from groq import Groq
import cv2
import base64
import os
from config import GROQ_API_KEY
from modules.iot_controller import get_frame
from modules.speech_manager import speak_text


def encode_image_from_frame(frame, output_path="captured_frame.jpg"):
    """
    Saves the frame and encodes it to base64 for API transmission.
    
    Args:
        frame (numpy.ndarray): Captured frame from camera
        output_path (str): Path to save the captured frame
    
    Returns:
        str: Base64 encoded image string
    """
    try:
        cv2.imwrite(output_path, frame)  # Save the frame
        with open(output_path, "rb") as image_file:
            encoded_image = base64.b64encode(image_file.read()).decode("utf-8")
        
        # Clean up saved file
        if os.path.exists(output_path):
            os.unlink(output_path)
        
        return encoded_image
    except Exception as e:
        print(f"Error encoding image: {e}")
        return None


def extract_text_from_image():
    """
    Captures an image and extracts all text content using Groq's Vision Model.
    
    Returns:
        str: Extracted text content or None if extraction failed
    """
    try:
        # Capture the frame
        frame = get_frame()
        if frame is None:
            print("Failed to capture image.")
            return None
        
        # Encode image to base64
        base64_image = encode_image_from_frame(frame)
        if not base64_image:
            print("Failed to encode image.")
            return None

        # Initialize Groq client
        client = Groq(api_key=GROQ_API_KEY)

        # Send the image to Groq's Vision Model
        chat_completion = client.chat.completions.create(
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": (
                                "Analyze the image and extract all text. "
                                "I don't need a description of the image, only extract the text from the image. "
                                "If no text is detected, print 'no text'. "
                                "If it contains dates, numbers, or addresses, extract them with proper context."
                            ),
                        },
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{base64_image}",
                            },
                        },
                    ],
                }
            ],
            model="llama-3.2-11b-vision-preview",
        )

        # Extract and return the response
        extracted_text = chat_completion.choices[0].message.content
        print("Extracted Text:", extracted_text)
        speak_text(extracted_text)
        return extracted_text
        
    except Exception as e:
        print(f"Error in text extraction: {e}")
        return None


def extract_text_with_context(context_description):
    """
    Extracts text from an image with specific context focus.
    
    Args:
        context_description (str): Description of what type of text to focus on
    
    Returns:
        str: Extracted text content or None if extraction failed
    """
    try:
        # Capture the frame
        frame = get_frame()
        if frame is None:
            print("Failed to capture image.")
            return None
        
        # Encode image to base64
        base64_image = encode_image_from_frame(frame)
        if not base64_image:
            print("Failed to encode image.")
            return None

        # Initialize Groq client
        client = Groq(api_key=GROQ_API_KEY)

        # Send the image to Groq's Vision Model with context
        chat_completion = client.chat.completions.create(
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": f"Focus on extracting text related to: {context_description}. "
                                   "Extract only the relevant text content, not image descriptions.",
                        },
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{base64_image}",
                            },
                        },
                    ],
                }
            ],
            model="llama-3.2-11b-vision-preview",
        )

        # Extract and return the response
        extracted_text = chat_completion.choices[0].message.content
        print("Contextual Text Extraction:", extracted_text)
        speak_text(extracted_text)
        return extracted_text
        
    except Exception as e:
        print(f"Error in contextual text extraction: {e}")
        return None


def extract_structured_data():
    """
    Extracts structured data like forms, tables, or organized text from images.
    
    Returns:
        str: Structured data content or None if extraction failed
    """
    try:
        # Capture the frame
        frame = get_frame()
        if frame is None:
            print("Failed to capture image.")
            return None
        
        # Encode image to base64
        base64_image = encode_image_from_frame(frame)
        if not base64_image:
            print("Failed to encode image.")
            return None

        # Initialize Groq client
        client = Groq(api_key=GROQ_API_KEY)

        # Send the image to Groq's Vision Model for structured data extraction
        chat_completion = client.chat.completions.create(
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": (
                                "Extract structured data from this image. "
                                "If there are forms, tables, or organized text, "
                                "present them in a clear, structured format. "
                                "Focus on maintaining the organization and relationships between data elements."
                            ),
                        },
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{base64_image}",
                            },
                        },
                    ],
                }
            ],
            model="llama-3.2-11b-vision-preview",
        )

        # Extract and return the response
        structured_data = chat_completion.choices[0].message.content
        print("Structured Data:", structured_data)
        speak_text(structured_data)
        return structured_data
        
    except Exception as e:
        print(f"Error in structured data extraction: {e}")
        return None
