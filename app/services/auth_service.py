import httpx
from typing import Optional, Dict, Any
from urllib.parse import urlencode
from app.config import settings

class GoogleAuthService:
    """Service to handle Google OAuth authentication"""
    
    def __init__(self):
        self.client_id = settings.google_client_id
        self.client_secret = settings.google_client_secret
        self.redirect_uri = settings.google_redirect_uri
        self.auth_url = settings.google_auth_url
        self.token_url = settings.google_token_url
        self.user_info_url = settings.google_user_info_url
    
    def get_authorization_url(self, state: Optional[str] = None) -> str:
        """Generate Google OAuth authorization URL"""
        params = {
            "client_id": self.client_id,
            "redirect_uri": self.redirect_uri,
            "scope": "openid email profile",
            "response_type": "code",
            "access_type": "offline",
            "prompt": "consent",
        }
        
        if state:
            params["state"] = state
        
        return f"{self.auth_url}?{urlencode(params)}"
    
    async def exchange_code_for_token(self, code: str) -> Optional[Dict[str, Any]]:
        """Exchange authorization code for access token"""
        data = {
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "code": code,
            "grant_type": "authorization_code",
            "redirect_uri": self.redirect_uri,
        }
        
        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(self.token_url, data=data)
                response.raise_for_status()
                return response.json()
            except httpx.HTTPError:
                return None
    
    async def get_user_info(self, access_token: str) -> Optional[Dict[str, Any]]:
        """Get user information from Google"""
        headers = {"Authorization": f"Bearer {access_token}"}
        
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(self.user_info_url, headers=headers)
                response.raise_for_status()
                return response.json()
            except httpx.HTTPError:
                return None

# Global instance
google_auth_service = GoogleAuthService()