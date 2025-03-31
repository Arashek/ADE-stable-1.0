from fastapi import APIRouter, HTTPException, Depends, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from typing import List, Optional, Dict
from datetime import datetime, timedelta
from jose import JWTError, jwt
from passlib.context import CryptContext
from pydantic import BaseModel
import os
from enum import Enum
from ...core.auth.auth_service import AuthService
from ...core.auth.two_factor import TwoFactorAuth
from ...core.models.user import User

# Router setup
router = APIRouter(
    prefix="/auth",
    tags=["authentication"]
)

# Models
class UserRole(str, Enum):
    ADMIN = "admin"
    DEVELOPER = "developer"
    VIEWER = "viewer"

class Token(BaseModel):
    access_token: str
    token_type: str
    expires_in: int
    roles: List[UserRole]

class TokenData(BaseModel):
    username: Optional[str] = None
    roles: List[UserRole] = []

class User(BaseModel):
    username: str
    email: Optional[str] = None
    full_name: Optional[str] = None
    disabled: bool = False
    roles: List[UserRole] = [UserRole.VIEWER]

class UserInDB(User):
    hashed_password: str

class TwoFactorSetupRequest(BaseModel):
    method: str  # "totp", "sms", or "email"
    phone_number: Optional[str] = None
    email: Optional[str] = None

class TwoFactorVerifyRequest(BaseModel):
    code: str
    method: str

# Security configuration
SECRET_KEY = os.getenv("JWT_SECRET_KEY", "your-secret-key-here")  # Use env var in production
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))

# Password handling
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/token")

# Mock database - replace with real DB in production
fake_users_db = {
    "admin": {
        "username": "admin",
        "full_name": "Admin User",
        "email": "admin@example.com",
        "hashed_password": pwd_context.hash("admin"),
        "disabled": False,
        "roles": [UserRole.ADMIN, UserRole.DEVELOPER, UserRole.VIEWER]
    },
    "developer": {
        "username": "developer",
        "full_name": "Developer User",
        "email": "dev@example.com",
        "hashed_password": pwd_context.hash("developer"),
        "disabled": False,
        "roles": [UserRole.DEVELOPER, UserRole.VIEWER]
    },
    "viewer": {
        "username": "viewer",
        "full_name": "Viewer User",
        "email": "viewer@example.com",
        "hashed_password": pwd_context.hash("viewer"),
        "disabled": False,
        "roles": [UserRole.VIEWER]
    }
}

# Helper functions
def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

def get_user(db, username: str):
    if username in db:
        user_dict = db[username]
        return UserInDB(**user_dict)
    return None

def authenticate_user(db, username: str, password: str):
    user = get_user(db, username)
    if not user:
        return False
    if not verify_password(password, user.hashed_password):
        return False
    return user

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

async def get_current_user(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        
        # Extract roles from the token
        roles_data = payload.get("roles", [])
        token_data = TokenData(username=username, roles=roles_data)
    except JWTError:
        raise credentials_exception
    
    user = get_user(fake_users_db, username=token_data.username)
    if user is None:
        raise credentials_exception
    
    # Ensure the token's roles match the user's current roles
    if set(roles_data) != set(user.roles):
        # Token has outdated roles
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Token contains outdated permissions",
        )
    
    return user

async def get_current_active_user(current_user: User = Depends(get_current_user)):
    if current_user.disabled:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user

# Role-based access control
def has_role(required_roles: List[UserRole]):
    async def role_checker(current_user: User = Depends(get_current_active_user)):
        for role in required_roles:
            if role in current_user.roles:
                return current_user
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Insufficient permissions. Required roles: {required_roles}"
        )
    return role_checker

# Auth endpoints
@router.post("/token", response_model=Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    user = authenticate_user(fake_users_db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Include roles in the token
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username, "roles": [role for role in user.roles]},
        expires_delta=access_token_expires
    )
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "expires_in": ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        "roles": user.roles
    }

@router.get("/me", response_model=User)
async def read_users_me(current_user: User = Depends(get_current_active_user)):
    return current_user

# Admin-only endpoint
@router.get("/users", response_model=List[User])
async def read_users(current_user: User = Depends(has_role([UserRole.ADMIN]))):
    users = []
    for username, user_data in fake_users_db.items():
        user = User(
            username=user_data["username"],
            email=user_data["email"],
            full_name=user_data["full_name"],
            disabled=user_data["disabled"],
            roles=user_data["roles"]
        )
        users.append(user)
    return users

# Create new user (admin only)
@router.post("/users", response_model=User)
async def create_user(
    username: str,
    password: str,
    email: Optional[str] = None,
    full_name: Optional[str] = None,
    roles: List[UserRole] = [UserRole.VIEWER],
    current_user: User = Depends(has_role([UserRole.ADMIN]))
):
    if username in fake_users_db:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already registered"
        )
    
    hashed_password = get_password_hash(password)
    fake_users_db[username] = {
        "username": username,
        "email": email,
        "full_name": full_name,
        "hashed_password": hashed_password,
        "disabled": False,
        "roles": roles
    }
    
    return User(
        username=username,
        email=email,
        full_name=full_name,
        roles=roles
    )

@router.post("/2fa/setup")
async def setup_2fa(
    request: TwoFactorSetupRequest,
    current_user: User = Depends(get_current_user),
    auth_service: AuthService = Depends(get_auth_service),
    two_factor_auth: TwoFactorAuth = Depends(get_two_factor_auth)
):
    """Set up 2FA for a user."""
    if request.method == "totp":
        # Generate TOTP secret and QR code
        secret = two_factor_auth.generate_totp_secret(current_user.id)
        qr_code = two_factor_auth.get_totp_qr(current_user.id, current_user.email)
        return {
            "secret": secret,
            "qr_code": qr_code
        }
    elif request.method == "sms":
        if not request.phone_number:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Phone number required for SMS 2FA"
            )
        success = await two_factor_auth.send_sms_code(current_user.id, request.phone_number)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to send SMS code"
            )
        return {"message": "SMS code sent"}
    elif request.method == "email":
        if not request.email:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email required for email 2FA"
            )
        success = await two_factor_auth.send_email_code(current_user.id, request.email)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to send email code"
            )
        return {"message": "Email code sent"}
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid 2FA method"
        )

@router.post("/2fa/verify")
async def verify_2fa(
    request: TwoFactorVerifyRequest,
    current_user: User = Depends(get_current_user),
    two_factor_auth: TwoFactorAuth = Depends(get_two_factor_auth)
):
    """Verify 2FA code."""
    if request.method == "totp":
        if not two_factor_auth.verify_totp(current_user.id, request.code):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid TOTP code"
            )
    elif request.method in ["sms", "email"]:
        if not two_factor_auth.verify_code(current_user.id, request.code):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid verification code"
            )
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid 2FA method"
        )
        
    return {"message": "2FA verified successfully"}

@router.get("/2fa/status")
async def get_2fa_status(
    current_user: User = Depends(get_current_user),
    two_factor_auth: TwoFactorAuth = Depends(get_two_factor_auth)
):
    """Get 2FA status for current user."""
    return {
        "enabled": two_factor_auth.is_2fa_enabled(current_user.id)
    } 