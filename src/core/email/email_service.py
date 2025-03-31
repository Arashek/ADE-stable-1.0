from typing import Optional
import aiosmtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from ..config import settings

class EmailService:
    def __init__(self):
        self.smtp_host = settings.SMTP_HOST
        self.smtp_port = settings.SMTP_PORT
        self.smtp_username = settings.SMTP_USERNAME
        self.smtp_password = settings.SMTP_PASSWORD
        self.from_email = settings.FROM_EMAIL
        self.from_name = settings.FROM_NAME

    async def send_email(
        self,
        to_email: str,
        subject: str,
        html_content: str,
        text_content: Optional[str] = None
    ):
        """Send an email using SMTP"""
        try:
            message = MIMEMultipart("alternative")
            message["Subject"] = subject
            message["From"] = f"{self.from_name} <{self.from_email}>"
            message["To"] = to_email

            # Add HTML content
            message.attach(MIMEText(html_content, "html"))

            # Add plain text content if provided
            if text_content:
                message.attach(MIMEText(text_content, "plain"))

            # Connect to SMTP server and send email
            async with aiosmtplib.SMTP(
                hostname=self.smtp_host,
                port=self.smtp_port,
                use_tls=True
            ) as smtp:
                await smtp.login(self.smtp_username, self.smtp_password)
                await smtp.send_message(message)

        except Exception as e:
            # Log the error but don't raise it to prevent blocking the main flow
            print(f"Failed to send email: {str(e)}")

    async def send_confirmation_email(
        self,
        email: str,
        name: Optional[str] = None,
        position: Optional[int] = None
    ):
        """Send confirmation email after early access signup"""
        subject = "Welcome to the CloudEV.ai Early Access Program!"
        
        # Create personalized greeting
        greeting = f"Hi {name}," if name else "Hi there,"
        
        # Create position message
        position_msg = (
            f"You are currently #{position} on our waitlist."
            if position
            else "You are now on our waitlist."
        )

        html_content = f"""
        <html>
            <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
                <h1 style="color: #2c3e50;">Welcome to CloudEV.ai!</h1>
                <p>{greeting}</p>
                <p>Thank you for joining our early access program. We're excited to have you on board!</p>
                <p>{position_msg}</p>
                <p>We'll keep you updated on your status and send you an invitation when it's your turn to join.</p>
                <p>In the meantime, you can:</p>
                <ul>
                    <li>Follow us on Twitter for updates</li>
                    <li>Join our Discord community</li>
                    <li>Check your waitlist status anytime</li>
                </ul>
                <p>Best regards,<br>The CloudEV.ai Team</p>
            </body>
        </html>
        """

        text_content = f"""
        Welcome to CloudEV.ai!

        {greeting}

        Thank you for joining our early access program. We're excited to have you on board!

        {position_msg}

        We'll keep you updated on your status and send you an invitation when it's your turn to join.

        In the meantime, you can:
        - Follow us on Twitter for updates
        - Join our Discord community
        - Check your waitlist status anytime

        Best regards,
        The CloudEV.ai Team
        """

        await self.send_email(email, subject, html_content, text_content)

    async def send_invitation_email(
        self,
        email: str,
        invitation_code: str,
        custom_message: Optional[str] = None
    ):
        """Send invitation email with access code"""
        subject = "Your CloudEV.ai Early Access Invitation"
        
        # Create personalized message
        custom_msg = f"<p>{custom_message}</p>" if custom_message else ""

        html_content = f"""
        <html>
            <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
                <h1 style="color: #2c3e50;">You're Invited to CloudEV.ai!</h1>
                <p>Congratulations! Your early access invitation is ready.</p>
                {custom_msg}
                <p>Your invitation code is:</p>
                <div style="background-color: #f8f9fa; padding: 15px; border-radius: 5px; font-size: 24px; font-weight: bold; text-align: center; margin: 20px 0;">
                    {invitation_code}
                </div>
                <p>Click the button below to get started:</p>
                <div style="text-align: center; margin: 30px 0;">
                    <a href="{settings.APP_URL}/register?code={invitation_code}" 
                       style="background-color: #3498db; color: white; padding: 12px 24px; text-decoration: none; border-radius: 5px; font-weight: bold;">
                        Create Your Account
                    </a>
                </div>
                <p>This invitation code is unique to you and can only be used once.</p>
                <p>If you have any questions, please don't hesitate to reach out to our support team.</p>
                <p>Best regards,<br>The CloudEV.ai Team</p>
            </body>
        </html>
        """

        text_content = f"""
        You're Invited to CloudEV.ai!

        Congratulations! Your early access invitation is ready.

        {custom_message if custom_message else ""}

        Your invitation code is:
        {invitation_code}

        Click here to create your account:
        {settings.APP_URL}/register?code={invitation_code}

        This invitation code is unique to you and can only be used once.

        If you have any questions, please don't hesitate to reach out to our support team.

        Best regards,
        The CloudEV.ai Team
        """

        await self.send_email(email, subject, html_content, text_content)

# Create a global instance
email_service = EmailService() 