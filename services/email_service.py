"""
Email Service for sending newsletter notifications
Supports HTML emails with embedded images
"""
import os
import smtplib
import base64
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.image import MIMEImage
from pathlib import Path
from typing import Optional, List
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class EmailConfig:
    """Email configuration"""
    def __init__(
        self,
        smtp_host: str = "smtp.gmail.com",
        smtp_port: int = 587,
        sender_email: str = "",
        sender_password: str = "",
        sender_name: str = "Open Pulse Newsletter",
    ):
        self.smtp_host = smtp_host
        self.smtp_port = smtp_port
        self.sender_email = sender_email
        self.sender_password = sender_password
        self.sender_name = sender_name
    
    @classmethod
    def from_env(cls):
        """Load configuration from environment variables"""
        return cls(
            smtp_host=os.getenv("SMTP_HOST", "smtp.gmail.com"),
            smtp_port=int(os.getenv("SMTP_PORT", "587")),
            sender_email=os.getenv("SENDER_EMAIL", ""),
            sender_password=os.getenv("SENDER_PASSWORD", ""),
            sender_name=os.getenv("SENDER_NAME", "Open Pulse Newsletter"),
        )


class EmailService:
    """Service for sending newsletter emails"""
    
    def __init__(self, config: EmailConfig):
        self.config = config
    
    def send_newsletter(
        self,
        recipients: List[str],
        newsletter_content: str,
        cover_image_path: Optional[str] = None,
        subject: Optional[str] = None,
    ) -> bool:
        """
        Send newsletter email with embedded cover image
        
        Args:
            recipients: List of recipient email addresses
            newsletter_content: Newsletter content (markdown/text)
            cover_image_path: Path to cover image file (optional)
            subject: Email subject (optional, auto-generated if not provided)
        
        Returns:
            True if sent successfully, False otherwise
        """
        if not self.config.sender_email or not self.config.sender_password:
            print("❌ Email credentials not configured")
            return False
        
        if not recipients:
            print("❌ No recipients specified")
            return False
        
        # Generate subject if not provided
        if not subject:
            subject = f"📰 Your Personalized Newsletter - {datetime.now().strftime('%B %d, %Y')}"
        
        try:
            # Create message
            msg = MIMEMultipart('related')
            msg['Subject'] = subject
            msg['From'] = f"{self.config.sender_name} <{self.config.sender_email}>"
            msg['To'] = ", ".join(recipients)
            
            # Create HTML content
            html_content = self._create_html_content(newsletter_content, cover_image_path)
            
            # Attach HTML content
            html_part = MIMEText(html_content, 'html', 'utf-8')
            msg.attach(html_part)
            
            # Embed cover image if provided
            if cover_image_path and os.path.exists(cover_image_path):
                with open(cover_image_path, 'rb') as img_file:
                    img_data = img_file.read()
                    image = MIMEImage(img_data)
                    image.add_header('Content-ID', '<cover_image>')
                    image.add_header('Content-Disposition', 'inline', filename=os.path.basename(cover_image_path))
                    msg.attach(image)
            
            # Send email
            with smtplib.SMTP(self.config.smtp_host, self.config.smtp_port) as server:
                server.starttls()
                server.login(self.config.sender_email, self.config.sender_password)
                server.send_message(msg)
            
            print(f"✅ Newsletter sent to {len(recipients)} recipient(s)")
            return True
            
        except Exception as e:
            print(f"❌ Failed to send email: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def _create_html_content(self, newsletter_content: str, cover_image_path: Optional[str]) -> str:
        """Create HTML email content with embedded image"""
        
        # Convert markdown-style content to HTML (basic conversion)
        html_content = newsletter_content.replace('\n\n', '</p><p>').replace('\n', '<br>')
        
        # Add cover image if available
        cover_image_html = ""
        if cover_image_path and os.path.exists(cover_image_path):
            cover_image_html = '''
            <div style="text-align: center; margin: 30px 0;">
                <img src="cid:cover_image" alt="Newsletter Cover" style="max-width: 100%; height: auto; border-radius: 8px; box-shadow: 0 4px 6px rgba(0,0,0,0.1);">
            </div>
            '''
        
        html_template = f'''
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Newsletter</title>
        </head>
        <body style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif; line-height: 1.6; color: #333; max-width: 600px; margin: 0 auto; padding: 20px; background-color: #f5f5f5;">
            
            <!-- Header -->
            <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 30px; border-radius: 10px 10px 0 0; text-align: center;">
                <h1 style="margin: 0; font-size: 28px; font-weight: 600;">📰 Open Pulse Newsletter</h1>
                <p style="margin: 10px 0 0 0; opacity: 0.9; font-size: 14px;">Your Personalized AI-Generated Newsletter</p>
            </div>
            
            <!-- Content -->
            <div style="background: white; padding: 40px; border-radius: 0 0 10px 10px; box-shadow: 0 2px 4px rgba(0,0,0,0.1);">
                
                {cover_image_html}
                
                <div style="color: #444; font-size: 16px; line-height: 1.8;">
                    <p>{html_content}</p>
                </div>
                
                <!-- Divider -->
                <hr style="border: none; border-top: 1px solid #e0e0e0; margin: 30px 0;">
                
                <!-- Footer -->
                <div style="text-align: center; color: #888; font-size: 12px;">
                    <p>Generated by <strong>Open Pulse</strong> - Your AI Newsletter Assistant</p>
                    <p style="margin: 10px 0; color: #aaa;">
                        {datetime.now().strftime('%B %d, %Y at %I:%M %p')}
                    </p>
                </div>
            </div>
            
        </body>
        </html>
        '''
        
        return html_template


def send_newsletter_email(
    newsletter_content: str,
    cover_image_path: Optional[str] = None,
    recipients: Optional[List[str]] = None,
) -> bool:
    """
    Convenience function to send newsletter email

    Args:
        newsletter_content: Newsletter content
        cover_image_path: Path to cover image
        recipients: List of recipient emails (required)

    Returns:
        True if sent successfully
    """
    # Load config from environment
    config = EmailConfig.from_env()

    # Check if recipients provided
    if not recipients:
        print("⚠️  No recipients specified, skipping email")
        return False

    # Create service and send
    service = EmailService(config)
    return service.send_newsletter(
        recipients=recipients,
        newsletter_content=newsletter_content,
        cover_image_path=cover_image_path,
    )


if __name__ == "__main__":
    # Test email service
    test_content = """
    # Welcome to Your Newsletter!
    
    Here are today's top stories:
    
    ## AI Breakthrough
    Scientists have developed a new AI model that can...
    
    ## Space Exploration
    NASA announces plans for...
    
    ## Technology Trends
    The latest developments in quantum computing...
    """
    
    # Test with dummy data
    config = EmailConfig.from_env()
    service = EmailService(config)
    
    print("Testing email service...")
    print(f"SMTP Host: {config.smtp_host}")
    print(f"Sender: {config.sender_email}")
    print(f"Recipients: {os.getenv('DEFAULT_RECIPIENTS', 'Not set')}")

