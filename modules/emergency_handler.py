"""
Emergency Handler Module
Handles emergency situations by sending SOS messages with location information.
"""

from twilio.rest import Client
import requests
from config import (
    TWILIO_ACCOUNT_SID, 
    TWILIO_AUTH_TOKEN, 
    TWILIO_PHONE_NUMBER, 
    EMERGENCY_PHONE_NUMBER
)


def get_location():
    """
    Retrieves current location information using IP geolocation.
    
    Returns:
        str: Formatted location string with coordinates and Google Maps link
    """
    try:
        response = requests.get("https://ipinfo.io/json", timeout=10)
        data = response.json()
        
        location = data.get("loc", "Unknown location")  # lat,long
        city = data.get("city", "Unknown city")
        region = data.get("region", "Unknown region")
        country = data.get("country", "Unknown country")
        
        # Create Google Maps Link
        maps_link = "Location unavailable"
        if location != "Unknown location":
            maps_link = f"https://www.google.com/maps?q={location}"
        
        location_info = f"{city}, {region}, {country}\n📍 Location: {location}\n🔗 Google Maps: {maps_link}"
        return location_info
        
    except Exception as e:
        print(f"Error getting location: {e}")
        return "Location unavailable"


def send_sos_message():
    """
    Sends an SOS message via Twilio SMS with current location information.
    
    Returns:
        str: Message SID if successful, error message if failed
    """
    try:
        # Initialize Twilio client
        client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
        
        # Get current location
        location = get_location()
        
        # Compose emergency message
        message_body = f"🚨 SOS Alert 🚨\nPlease send help!\nLocation: {location}"
        
        # Send the message
        message = client.messages.create(
            from_=TWILIO_PHONE_NUMBER,
            body=message_body,
            to=EMERGENCY_PHONE_NUMBER
        )
        
        print(f"SOS message sent successfully. SID: {message.sid}")
        return message.sid
        
    except Exception as e:
        error_msg = f"Failed to send SOS message: {e}"
        print(error_msg)
        return error_msg


def send_custom_emergency_message(custom_message):
    """
    Sends a custom emergency message with location information.
    
    Args:
        custom_message (str): Custom message to include in the SOS alert
    
    Returns:
        str: Message SID if successful, error message if failed
    """
    try:
        # Initialize Twilio client
        client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
        
        # Get current location
        location = get_location()
        
        # Compose custom emergency message
        message_body = f"🚨 Emergency Alert 🚨\n{custom_message}\nLocation: {location}"
        
        # Send the message
        message = client.messages.create(
            from_=TWILIO_PHONE_NUMBER,
            body=message_body,
            to=EMERGENCY_PHONE_NUMBER
        )
        
        print(f"Custom emergency message sent successfully. SID: {message.sid}")
        return message.sid
        
    except Exception as e:
        error_msg = f"Failed to send custom emergency message: {e}"
        print(error_msg)
        return error_msg


def check_emergency_contacts():
    """
    Checks if emergency contact information is properly configured.
    
    Returns:
        dict: Status of emergency contact configuration
    """
    status = {
        'twilio_configured': bool(TWILIO_ACCOUNT_SID and TWILIO_AUTH_TOKEN),
        'phone_numbers_configured': bool(TWILIO_PHONE_NUMBER and EMERGENCY_PHONE_NUMBER),
        'account_sid': TWILIO_ACCOUNT_SID[:10] + "..." if TWILIO_ACCOUNT_SID else "Not configured",
        'from_number': TWILIO_PHONE_NUMBER,
        'to_number': EMERGENCY_PHONE_NUMBER
    }
    
    return status


def test_emergency_system():
    """
    Tests the emergency system without sending actual SOS messages.
    
    Returns:
        dict: Test results for various emergency system components
    """
    test_results = {
        'location_service': False,
        'twilio_connection': False,
        'message_composition': False
    }
    
    try:
        # Test location service
        location = get_location()
        test_results['location_service'] = location != "Location unavailable"
        
        # Test Twilio connection
        client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
        # Try to fetch account info to test connection
        account = client.api.accounts(TWILIO_ACCOUNT_SID).fetch()
        test_results['twilio_connection'] = account is not None
        
        # Test message composition
        test_message = f"Test message - Location: {location}"
        test_results['message_composition'] = len(test_message) > 0
        
    except Exception as e:
        print(f"Emergency system test failed: {e}")
    
    return test_results
