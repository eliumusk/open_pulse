"""
Services module for Open Pulse
"""
from .email_service import EmailService, EmailConfig, send_newsletter_email

__all__ = ["EmailService", "EmailConfig", "send_newsletter_email"]

