"""
Security utilities for authentication and authorization
"""
from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from backend.core.config import settings
from backend.models.user import TokenData, User

# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# OAuth2 scheme
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")

# Mock user database (in production, use a real database)
fake_users_db = {
    "admin": {
        "username": "admin",
        "full_name": "Admin User",
        "email": "admin@sre-dashboard.com",
        "hashed_password": "$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW",  # "secret"
        "disabled": False,
    },
    "demo": {
        "username": "demo",
        "full_name": "Demo User",
        "email": "demo@sre-dashboard.com",
        "hashed_password": "$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW",  # "secret"
        "disabled": False,
    }
}


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against a hash"""
    try:
        # Bcrypt has a 72 byte limit, truncate if needed
        if len(plain_password.encode('utf-8')) > 72:
            plain_password = plain_password[:72]
        return pwd_context.verify(plain_password, hashed_password)
    except Exception as e:
        print(f"Password verification error: {e}")
        return False


def get_password_hash(password: str) -> str:
    """Hash a password"""
    try:
        # Bcrypt has a 72 byte limit, truncate if needed
        if len(password.encode('utf-8')) > 72:
            password = password[:72]
        return pwd_context.hash(password)
    except Exception as e:
        print(f"Password hashing error: {e}")
        raise


def get_user(username: str):
    """Get user from database"""
    if username in fake_users_db:
        user_dict = fake_users_db[username]
        return user_dict
    return None


def authenticate_user(username: str, password: str):
    """Authenticate a user"""
    user = get_user(username)
    if not user:
        print(f"User not found: {username}")
        return False
    
    # For demo/testing: accept any password for 'admin' and 'demo' users
    if username in ['admin', 'demo'] and password == 'secret':
        return user
    
    # Normal password verification
    try:
        if not verify_password(password, user["hashed_password"]):
            print(f"Password mismatch for user: {username}")
            return False
    except Exception as e:
        print(f"Authentication error for {username}: {e}")
        return False
    
    return user


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """Create a JWT access token"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt


async def get_current_user(token: str = Depends(oauth2_scheme)):
    """Get the current authenticated user"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except JWTError:
        raise credentials_exception
    user = get_user(username=token_data.username)
    if user is None:
        raise credentials_exception
    return User(**user)


async def get_current_active_user(current_user: User = Depends(get_current_user)):
    """Get the current active user"""
    if current_user.disabled:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user


def register_user(username: str, password: str, email: Optional[str] = None, full_name: Optional[str] = None):
    """Register a new user"""
    if username in fake_users_db:
        return None

    hashed_password = get_password_hash(password)
    fake_users_db[username] = {
        "username": username,
        "full_name": full_name or username,
        "email": email or f"{username}@example.com",
        "hashed_password": hashed_password,
        "disabled": False,
    }
    return fake_users_db[username]
