"""
Speech Manager Module
Handles voice input (speech-to-text) and output (text-to-speech) functionality.
"""

import pyaudio
import wave
import pyttsx3
import warnings
from google.cloud import speech_v1 as speech
import os
import tempfile
from config import GOOGLE_CLOUD_CREDENTIALS_PATH, RECORDING_DURATION, SAMPLE_RATE

# Suppress warnings
warnings.simplefilter("ignore", category=FutureWarning)

# Initialize Google Speech-to-Text client
client = speech.SpeechClient.from_service_account_file(GOOGLE_CLOUD_CREDENTIALS_PATH)


def record_audio(output_file, duration=RECORDING_DURATION, sample_rate=SAMPLE_RATE):
    """
    Records audio from the microphone and saves it as a WAV file.
    
    Args:
        output_file (str): Path to save the recorded audio file
        duration (int): Recording duration in seconds (default: 5)
        sample_rate (int): Audio sample rate in Hz (default: 16000)
    
    Returns:
        bool: True if recording successful, False otherwise
    """
    chunk = 1024  # Buffer size
    format = pyaudio.paInt16  # 16-bit format
    channels = 1  # Mono
    rate = sample_rate  # Sample rate

    try:
        p = pyaudio.PyAudio()
        stream = p.open(format=format, channels=channels, rate=rate, input=True, frames_per_buffer=chunk)
        
        print("Recording speech... Speak now!")
        frames = []
        for _ in range(0, int(rate / chunk * duration)):
            data = stream.read(chunk)
            frames.append(data)
        
        print("Recording finished.")

        stream.stop_stream()
        stream.close()
        p.terminate()

        with wave.open(output_file, "wb") as wf:
            wf.setnchannels(channels)
            wf.setsampwidth(p.get_sample_size(format))
            wf.setframerate(rate)
            wf.writeframes(b''.join(frames))
        
        return True
    except Exception as e:
        print(f"Error recording audio: {e}")
        return False


def transcribe_audio(input_file):
    """
    Transcribe speech from the recorded audio file using Google Cloud Speech-to-Text.
    
    Args:
        input_file (str): Path to the audio file to transcribe
    
    Returns:
        str: Transcribed text or None if transcription failed
    """
    try:
        with open(input_file, 'rb') as audio_file:
            content = audio_file.read()
            audio = speech.RecognitionAudio(content=content)
            config = speech.RecognitionConfig(
                encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,
                sample_rate_hertz=SAMPLE_RATE,
                language_code='en-US'  # English language code
            )
            
            response = client.recognize(config=config, audio=audio)
            
            for result in response.results:
                transcript = result.alternatives[0].transcript
                return transcript
            
            return None
    except Exception as e:
        print(f"Error transcribing audio: {e}")
        return None


def get_voice_input():
    """
    Records audio from microphone and converts it to text.
    
    Returns:
        str: Transcribed text from voice input or None if failed
    """
    try:
        # Create temporary file for recording
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as temp_file:
            temp_audio_path = temp_file.name
        
        # Record audio
        if record_audio(temp_audio_path, duration=RECORDING_DURATION):
            # Transcribe audio
            transcript = transcribe_audio(temp_audio_path)
            
            # Clean up temporary file
            os.unlink(temp_audio_path)
            
            return transcript
        else:
            return None
    except Exception as e:
        print(f"Error in voice input: {e}")
        return None


def speak_text(text):
    """
    Convert text to speech using pyttsx3.
    
    Args:
        text (str): Text to convert to speech
    """
    try:
        engine = pyttsx3.init()
        engine.say(text)
        engine.runAndWait()
    except Exception as e:
        print(f"Error in text-to-speech: {e}")
