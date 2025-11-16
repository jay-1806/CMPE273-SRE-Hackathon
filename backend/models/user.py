"""
User models for authentication
"""
from pydantic import BaseModel, EmailStr
from typing import Optional


class User(BaseModel):
    """User model"""
    username: str
    email: Optional[EmailStr] = None
    full_name: Optional[str] = None
    disabled: Optional[bool] = False


class UserInDB(User):
    """User model with hashed password"""
    hashed_password: str


class Token(BaseModel):
    """Token model"""
    access_token: str
    token_type: str


class TokenData(BaseModel):
    """Token data model"""
    username: Optional[str] = None


class UserLogin(BaseModel):
    """User login model"""
    username: str
    password: str


class UserRegister(BaseModel):
    """User registration model"""
    username: str
    password: str
    email: Optional[EmailStr] = None
    full_name: Optional[str] = None
