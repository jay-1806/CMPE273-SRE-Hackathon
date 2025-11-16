"""
Authentication API endpoints
"""
from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from backend.models.user import Token, User, UserLogin, UserRegister
from backend.utils.security import (
    authenticate_user,
    create_access_token,
    get_current_active_user,
    register_user,
)
from backend.core.config import settings
from backend.services.redis_service import cache

router = APIRouter(prefix="/api/auth", tags=["Authentication"])


# @router.post("/login", response_model=Token)
# async def login(form_data: OAuth2PasswordRequestForm = Depends()):
#     """Login endpoint"""
#     user = authenticate_user(form_data.username, form_data.password)
#     if not user:
#         raise HTTPException(
#             status_code=status.HTTP_401_UNAUTHORIZED,
#             detail="Incorrect username or password",
#             headers={"WWW-Authenticate": "Bearer"},
#         )

#     access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
#     access_token = create_access_token(
#         data={"sub": user["username"]}, expires_delta=access_token_expires
#     )

#     # Store session in cache
#     cache.set(f"session:{user['username']}", {
#         "username": user["username"],
#         "login_time": str(timedelta())
#     }, expire=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60)

#     return {"access_token": access_token, "token_type": "bearer"}

@router.post("/login", response_model=Token)
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    """Login endpoint"""
    try:
        print(f"Login attempt for user: {form_data.username}")  # Debug log
        
        user = authenticate_user(form_data.username, form_data.password)
        if not user:
            print(f"Authentication failed for: {form_data.username}")  # Debug log
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect username or password",
                headers={"WWW-Authenticate": "Bearer"},
            )

        access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={"sub": user["username"]}, expires_delta=access_token_expires
        )

        # Store session in cache
        cache.set(f"session:{user['username']}", {
            "username": user["username"],
            "login_time": str(timedelta())
        }, expire=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60)

        print(f"Login successful for: {user['username']}")  # Debug log
        return {"access_token": access_token, "token_type": "bearer"}
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Login error: {type(e).__name__}: {str(e)}")  # Debug log
        import traceback
        traceback.print_exc()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Login error: {str(e)}"
        )


@router.post("/register", response_model=dict)
async def register(user_data: UserRegister):
    """Register a new user"""
    user = register_user(
        username=user_data.username,
        password=user_data.password,
        email=user_data.email,
        full_name=user_data.full_name
    )

    if not user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already exists"
        )

    return {
        "message": "User registered successfully",
        "username": user["username"]
    }


@router.get("/me", response_model=User)
async def read_users_me(current_user: User = Depends(get_current_active_user)):
    """Get current user information"""
    return current_user


@router.post("/logout")
async def logout(current_user: User = Depends(get_current_active_user)):
    """Logout endpoint"""
    # Remove session from cache
    cache.delete(f"session:{current_user.username}")

    return {"message": "Logged out successfully"}
