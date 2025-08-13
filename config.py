"""
Configuration file for the AEye project.
Contains all API keys, configuration values, and environment variables.
"""
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Google Cloud Speech-to-Text API Key
GOOGLE_CLOUD_CREDENTIALS_PATH = os.getenv("GOOGLE_CLOUD_CREDENTIALS_PATH", "modules/elated-yen-446113-a9-e3c6f3910fa2.json")

# Google Generative AI API Key
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "Enter Gemini API Key here")

# Groq API Key
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "Enter GROQ API Key here")

# Twilio Configuration
TWILIO_ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID", "Enter TWILIO_ACCOUNT_SID here")
TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN", "Enter TWILIO_AUTH_TOKEN here")
TWILIO_PHONE_NUMBER = os.getenv("TWILIO_PHONE_NUMBER", "Enter TWILIO_PHONE_NUMBER here")
EMERGENCY_PHONE_NUMBER = os.getenv("EMERGENCY_PHONE_NUMBER", "Enter EMERGENCY_PHONE_NUMBER here")

# ESP32 Configuration
ESP32_CAM_URL = os.getenv("ESP32_CAM_URL", "http://192.168.168.232/cam-hi.jpg")
ESP32_SERVO_URL = os.getenv("ESP32_SERVO_URL", "http://192.168.168.193")

# Camera Configuration
CAMERA_INDEX = int(os.getenv("CAMERA_INDEX", "0"))
RECORDING_DURATION = int(os.getenv("RECORDING_DURATION", "5"))
SAMPLE_RATE = int(os.getenv("SAMPLE_RATE", "16000"))

# Face Recognition Configuration
FACE_OUTPUT_DIR = os.getenv("FACE_OUTPUT_DIR", "known_image")
FACE_DETECTION_SCALE_FACTOR = float(os.getenv("FACE_DETECTION_SCALE_FACTOR", "1.2"))
FACE_DETECTION_MIN_NEIGHBORS = int(os.getenv("FACE_DETECTION_MIN_NEIGHBORS", "6"))
FACE_DETECTION_MIN_SIZE = int(os.getenv("FACE_DETECTION_MIN_SIZE", "40"))

