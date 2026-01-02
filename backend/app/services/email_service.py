from datetime import datetime, timedelta
from typing import Optional
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from ..config import settings


class EmailService:
    """Service for sending emails via Gmail SMTP"""
    
    def __init__(self):
        self.gmail_user = settings.GMAIL_USER
        self.gmail_password = settings.GMAIL_APP_PASSWORD
        self.from_name = settings.EMAIL_FROM_NAME
        self.smtp_server = "smtp.gmail.com"
        self.smtp_port = 587
    
    def send_password_reset_email(self, to_email: str, reset_token: str) -> bool:
        """
        Send password reset email with verification link
        
        Args:
            to_email: Recipient email address
            reset_token: Password reset token
            
        Returns:
            bool: True if email sent successfully, False otherwise
        """
        try:
            # Create reset link
            reset_url = f"{settings.RESET_PASSWORD_URL}?token={reset_token}"
            
            # Create message
            message = MIMEMultipart("alternative")
            message["Subject"] = "Reset Your Password - AI Data Analyst"
            message["From"] = f"{self.from_name} <{self.gmail_user}>"
            message["To"] = to_email
            
            # Email body (HTML)
            html_body = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <style>
                    body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; line-height: 1.6; color: #333; }}
                    .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                    .header {{ background: linear-gradient(135deg, #0a0a0a 0%, #1a1a1a 100%); color: #5eaea6; padding: 30px; text-align: center; border-radius: 8px 8px 0 0; }}
                    .content {{ background: #ffffff; padding: 30px; border: 1px solid #e5e5e5; border-top: none; }}
                    .button {{ display: inline-block; padding: 12px 30px; background: #5eaea6; color: #ffffff; text-decoration: none; border-radius: 6px; margin: 20px 0; }}
                    .footer {{ text-align: center; padding: 20px; color: #999; font-size: 12px; }}
                    .warning {{ background: #fff3cd; border: 1px solid #ffc107; padding: 15px; border-radius: 6px; margin: 20px 0; }}
                </style>
            </head>
            <body>
                <div class="container">
                    <div class="header">
                        <h1>Password Reset Request</h1>
                    </div>
                    <div class="content">
                        <p>Hello,</p>
                        <p>We received a request to reset your password for your AI Data Analyst account.</p>
                        <p>Click the button below to reset your password:</p>
                        <p style="text-align: center;">
                            <a href="{reset_url}" class="button">Reset Password</a>
                        </p>
                        <p>Or copy and paste this link into your browser:</p>
                        <p style="word-break: break-all; color: #5eaea6;">{reset_url}</p>
                        
                        <div class="warning">
                            <strong>⚠️ This link will expire in 1 hour.</strong>
                        </div>
                        
                        <p>If you didn't request a password reset, you can safely ignore this email. Your password will remain unchanged.</p>
                        
                        <p>Best regards,<br>AI Data Analyst Team</p>
                    </div>
                    <div class="footer">
                        <p>Your data stays private. No training on your data.</p>
                        <p>This is an automated message, please do not reply.</p>
                    </div>
                </div>
            </body>
            </html>
            """
            
            # Attach HTML body
            html_part = MIMEText(html_body, "html")
            message.attach(html_part)
            
            # Send email
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.gmail_user, self.gmail_password)
                server.send_message(message)
            
            return True
            
        except Exception as e:
            print(f"Error sending email: {e}")
            return False


# Singleton instance
email_service = EmailService()
