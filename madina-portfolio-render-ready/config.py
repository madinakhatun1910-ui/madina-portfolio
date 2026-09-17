
import os
from pathlib import Path

class Config:
    SECRET_KEY = os.environ.get("MADINA_SECRET_KEY", "change-this-secret-key")
    # WhatsApp number lives here only. Use country code without + or spaces.
    WHATSAPP_NUMBER = os.environ.get("MADINA_WHATSAPP", "7004329376")
    PORTRAIT_IMAGE = os.environ.get("MADINA_PORTRAIT", "")
    # Email notifications for contact-form enquiries. Configure these environment variables
    # on the machine/server where the Flask app runs. No passwords are stored in source code.
    SMTP_HOST = os.environ.get("MADINA_SMTP_HOST", "smtp.gmail.com")
    SMTP_PORT = int(os.environ.get("MADINA_SMTP_PORT", "587"))
    SMTP_USERNAME = os.environ.get("MADINA_SMTP_USERNAME", "")
    SMTP_PASSWORD = os.environ.get("MADINA_SMTP_PASSWORD", "")
    NOTIFICATION_EMAIL = os.environ.get("MADINA_NOTIFICATION_EMAIL", "")
    SMTP_FROM = os.environ.get("MADINA_SMTP_FROM", "")

    SOCIALS = {
        "instagram": os.environ.get("MADINA_INSTAGRAM", ""),
        "youtube": os.environ.get("MADINA_YOUTUBE", ""),
        "linkedin": os.environ.get("MADINA_LINKEDIN", "")
    }
