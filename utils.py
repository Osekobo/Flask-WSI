import requests
import random
import os

# Generate  OTP


def generate_otp():
    return str(random.randint(1000, 9999))

# Format phone


def format_phone(phone):
    phone = phone.strip()
    if phone.startswith("0"):
        return "+254" + phone[1:]
    elif phone.startswith("+"):
        return phone
    else:
        raise ValueError("Invalid phone number format")

# Send SMS via Brevo


def send_sms_brevo(phone, message):
    BREVO_API_KEY = os.getenv("BREVO_API_KEY")
    if not BREVO_API_KEY:
        raise ValueError("BREVO_API_KEY is not set in environment variables")
    url = "https://api.brevo.com/v3/transactionalSMS/sms"
    headers = {
        "accept": "application/json",
        "api-key": BREVO_API_KEY,
        "content-type": "application/json"
    }
    payload = {
        "sender": "Techcamp",
        "recipient": phone,
        "content": message,
        "type": "transactional"
    }
    response = requests.post(url, headers=headers, json=payload)
    if response.status_code not in (200, 201):
        raise Exception(response.text)
    return response.json()

# Send Email via Brevo


def send_email_brevo(email, otp):
    if not email:
        raise ValueError("Email is required")
    BREVO_API_KEY = os.getenv("BREVO_API_KEY")
    if not BREVO_API_KEY:
        raise ValueError("BREVO_API_KEY is not set in environment variables")
    url = "https://api.brevo.com/v3/smtp/email"
    headers = {
        "accept": "application/json",
        "api-key": BREVO_API_KEY,
        "content-type": "application/json"
    }
    payload = {
        "sender": {"name": "Techcamp", "email": "collinsboseko2005@gmail.com"},
        "to": [{"email": email}],
        "subject": "Your OTP Code",
        "htmlContent": f"<p>Your OTP code is <strong>{otp}</strong></p>"
    }
    response = requests.post(url, headers=headers, json=payload)
    if response.status_code not in (200, 201):
        raise Exception(response.text)
    return response.json()

