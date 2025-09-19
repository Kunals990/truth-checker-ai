from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.responses import RedirectResponse, HTMLResponse
from sqlalchemy.orm import Session
from datetime import timedelta
from app.database import get_db
from app.services.auth_service import google_auth_service
from app.services.user_service import user_service
from app.schemas.user import UserCreate, Token, UserResponse
from app.utils.security import create_access_token
from app.middleware.auth_middleware import get_current_user
from app.config import settings
import secrets

router = APIRouter(prefix="/auth", tags=["authentication"])

# Store state tokens temporarily (in production, use Redis)
state_store = {}

@router.get("/login")
async def login():
    """Initiate Google OAuth login"""
    # Generate state token for CSRF protection
    state = secrets.token_urlsafe(32)
    
    # Store state (in production, use Redis with expiration)
    state_store[state] = True
    
    # Get authorization URL
    auth_url = google_auth_service.get_authorization_url(state)
    
    return {"auth_url": auth_url, "state": state}

@router.get("/callback")
async def auth_callback(code: str, state: str, db: Session = Depends(get_db)):
    """Handle Google OAuth callback"""
    
    # Verify state token
    if state not in state_store:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid state parameter"
        )
    
    # Remove used state token
    del state_store[state]
    
    # Exchange code for token
    token_data = await google_auth_service.exchange_code_for_token(code)
    if not token_data:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to exchange code for token"
        )
    
    # Get user info from Google
    user_info = await google_auth_service.get_user_info(token_data["access_token"])
    if not user_info:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to get user info"
        )
    
    # Check if user exists
    user = user_service.get_user_by_google_id(db, user_info["id"])
    
    if not user:
        # Create new user
        user_create = UserCreate(
            email=user_info["email"],
            name=user_info["name"],
            picture=user_info.get("picture"),
            google_id=user_info["id"]
        )
        user = user_service.create_user(db, user_create)
    
    # Create access token
    access_token_expires = timedelta(minutes=settings.access_token_expire_minutes)
    access_token = create_access_token(
        data={"sub": user.email},
        expires_delta=access_token_expires
    )
    
    # Redirect to frontend with token (for demo purposes)
    # In production, you might want to set an HTTP-only cookie instead
    redirect_url = f"/?access_token={access_token}&token_type=bearer"
    return RedirectResponse(url=redirect_url)

@router.post("/logout")
async def logout():
    """Logout user (client should delete token)"""
    return {"message": "Successfully logged out"}

@router.get("/me", response_model=UserResponse)
async def get_current_user_info(current_user = Depends(get_current_user)):
    """Get current user information"""
    return current_user