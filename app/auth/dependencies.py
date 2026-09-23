"""
Sana AI — Authentication Dependencies

Verifies Supabase access tokens and identifies
the authenticated Sana user.
"""

from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from supabase import Client, create_client

from app.core.config import settings


security = HTTPBearer()


supabase: Client = create_client(
    settings.supabase_url,
    settings.supabase_key,
)


async def verify_access_token(
    access_token: str,
) -> dict:
    """
    Verify a raw Supabase access token string and return the
    authenticated user's information.

    Shared by both the HTTP dependency below and the WebSocket
    live-voice endpoint, since WebSocket routes cannot use
    HTTPBearer/Depends-based header extraction the same way
    HTTP routes can.
    """

    try:
        response = supabase.auth.get_user(access_token)

        if not response or not response.user:
            raise HTTPException(
                status_code=401,
                detail="Invalid authentication token.",
            )

        user = response.user

        return {
            "id": str(user.id),
            "email": user.email,
            "access_token": access_token,
        }

    except HTTPException:
        raise

    except Exception as exc:
        raise HTTPException(
            status_code=401,
            detail="Authentication failed.",
        ) from exc


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
) -> dict:
    """
    Verify the Supabase access token and return
    the authenticated user's information.

    The access token is also returned so database
    operations can execute in the user's auth context.
    """

    return await verify_access_token(credentials.credentials)
    
