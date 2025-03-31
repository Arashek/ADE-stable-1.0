import pyotp
import qrcode
import io
import base64
from typing import Optional, Dict, Any
from datetime import datetime, timedelta
from fastapi import HTTPException, status
import aiohttp
import json
import logging

logger = logging.getLogger(__name__)

class TwoFactorAuth:
    def __init__(self, sms_api_key: Optional[str] = None, email_api_key: Optional[str] = None):
        self.sms_api_key = sms_api_key
        self.email_api_key = email_api_key
        self._totp_secrets: Dict[str, str] = {}
        self._verification_codes: Dict[str, Dict[str, Any]] = {}
        
    def generate_totp_secret(self, user_id: str) -> str:
        """Generate a new TOTP secret for a user."""
        secret = pyotp.random_base32()
        self._totp_secrets[user_id] = secret
        return secret
        
    def get_totp_qr(self, user_id: str, email: str) -> str:
        """Generate QR code for TOTP setup."""
        if user_id not in self._totp_secrets:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="TOTP secret not generated"
            )
            
        totp = pyotp.TOTP(self._totp_secrets[user_id])
        provisioning_uri = totp.provisioning_uri(email)
        
        # Generate QR code
        qr = qrcode.QRCode(version=1, box_size=10, border=5)
        qr.add_data(provisioning_uri)
        qr.make(fit=True)
        
        img = qr.make_image(fill_color="black", back_color="white")
        
        # Convert to base64
        buffered = io.BytesIO()
        img.save(buffered, format="PNG")
        return base64.b64encode(buffered.getvalue()).decode()
        
    def verify_totp(self, user_id: str, token: str) -> bool:
        """Verify a TOTP token."""
        if user_id not in self._totp_secrets:
            return False
            
        totp = pyotp.TOTP(self._totp_secrets[user_id])
        return totp.verify(token)
        
    async def send_sms_code(self, user_id: str, phone_number: str) -> bool:
        """Send SMS verification code."""
        if not self.sms_api_key:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="SMS API key not configured"
            )
            
        # Generate 6-digit code
        code = pyotp.random_base32()[:6]
        
        # Store code with expiration
        self._verification_codes[user_id] = {
            "code": code,
            "expires": datetime.utcnow() + timedelta(minutes=5),
            "method": "sms"
        }
        
        # Send SMS using your preferred SMS provider
        # This is a placeholder for actual SMS sending logic
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    "https://api.sms-provider.com/send",
                    headers={"Authorization": f"Bearer {self.sms_api_key}"},
                    json={
                        "to": phone_number,
                        "message": f"Your verification code is: {code}"
                    }
                ) as response:
                    return response.ok
        except Exception as e:
            logger.error(f"SMS sending failed: {str(e)}")
            return False
            
    async def send_email_code(self, user_id: str, email: str) -> bool:
        """Send email verification code."""
        if not self.email_api_key:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Email API key not configured"
            )
            
        # Generate 6-digit code
        code = pyotp.random_base32()[:6]
        
        # Store code with expiration
        self._verification_codes[user_id] = {
            "code": code,
            "expires": datetime.utcnow() + timedelta(minutes=5),
            "method": "email"
        }
        
        # Send email using your preferred email provider
        # This is a placeholder for actual email sending logic
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    "https://api.email-provider.com/send",
                    headers={"Authorization": f"Bearer {self.email_api_key}"},
                    json={
                        "to": email,
                        "subject": "Your Verification Code",
                        "text": f"Your verification code is: {code}"
                    }
                ) as response:
                    return response.ok
        except Exception as e:
            logger.error(f"Email sending failed: {str(e)}")
            return False
            
    def verify_code(self, user_id: str, code: str) -> bool:
        """Verify a code sent via SMS or email."""
        if user_id not in self._verification_codes:
            return False
            
        stored_data = self._verification_codes[user_id]
        
        # Check if code has expired
        if datetime.utcnow() > stored_data["expires"]:
            del self._verification_codes[user_id]
            return False
            
        # Verify code
        if stored_data["code"] == code:
            del self._verification_codes[user_id]
            return True
            
        return False
        
    def is_2fa_enabled(self, user_id: str) -> bool:
        """Check if 2FA is enabled for a user."""
        return user_id in self._totp_secrets or user_id in self._verification_codes 