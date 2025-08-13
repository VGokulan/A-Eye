"""
Main Application Module
Main entry point for the AI Eye Assistant application.
"""

from modules.speech_manager import get_voice_input, speak_text
from modules.scene_analyzer import analyze_scene
from modules.object_recognizer import recognize_object, handle_follow_up_queries
from modules.text_extractor import extract_text_from_image
from modules.emergency_handler import send_sos_message
from modules.face_recognition import register_new_face
from modules.navigation_assistant import analyze_environment
from modules.iot_controller import set_servo_angle


def start():
    """
    Main application loop that handles voice commands and triggers appropriate functions.
    """
    while True:
        print("Function is triggered")
        speak_text("Start to speak")
        
        while True:
            user_talk = get_voice_input()
            print(user_talk)  # Now returns text
            
            if user_talk:  # Ensure input is valid
                # Define trigger words for different functions
                scene_trigger = ["scene", "describe", "description", "seeing", "see"]
                sensory_trigger = ["sensory", "search", "holding", "buy"]
                ocr_trigger = ["read", "book", "notice", "pamphlet"]
                sos_trigger = ["sos", "emergency", "help"]
                face_trigger = ["face", "recognize", "register"]
                nav_trigger = ["navigation", "route", "navigate", "path", "show me route", "show me"]
                
                # Scene description trigger
                if any(word in user_talk for word in scene_trigger):
                    set_servo_angle(115)
                    scene_description = analyze_scene()
                    if scene_description:
                        speak_text(scene_description)
                    else:
                        speak_text("Failed to analyze scene")
                
                # Object recognition trigger
                if any(word in user_talk for word in sensory_trigger):
                    object_info = recognize_object()
                    if object_info:
                        handle_follow_up_queries(object_info)
                    else:
                        speak_text("Failed to recognize object")
                
                # Text extraction trigger
                if any(word in user_talk for word in ocr_trigger):
                    set_servo_angle(115)
                    extracted_text = extract_text_from_image()
                    if not extracted_text:
                        speak_text("Failed to extract text from image")
                
                # Emergency SOS trigger
                if any(word in user_talk for word in sos_trigger):
                    result = send_sos_message()
                    print(f"SOS Result: {result}")
                    if "SID" in str(result):
                        speak_text("SOS message sent successfully")
                    else:
                        speak_text("Failed to send SOS message")
                
                # Navigation trigger
                if any(word in user_talk for word in nav_trigger):
                    set_servo_angle(90)
                    navigation_info = analyze_environment()
                    if not navigation_info:
                        speak_text("Failed to analyze environment for navigation")
                
                # Face recognition trigger
                if any(word in user_talk for word in face_trigger):
                    set_servo_angle(90)
                    detected_name = register_new_face()
                    if detected_name:
                        speak_text(f"Face registered as {detected_name}")
                    else:
                        speak_text("Face registration failed.")
                
                # Exit command
                if "exit" in user_talk:
                    speak_text("Exiting now.")
                    return  # Stops the function
            else:
                speak_text("No Input")


if __name__ == "__main__":
    start()
