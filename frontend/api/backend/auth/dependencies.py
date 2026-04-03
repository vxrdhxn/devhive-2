from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from supabase import create_client, Client
try:
    from gotrue import User
except ImportError:
    from gotrue.types import User
from backend.config import get_settings
import anyio

settings = get_settings()

try:
    if settings.supabase_url and settings.supabase_url != "your_supabase_project_url" and settings.supabase_service_role_key:
        supabase: Client = create_client(
            settings.supabase_url,
            settings.supabase_service_role_key
        )
    else:
        supabase = None
except Exception as e:
    supabase = None
    print(f"Warning: Could not initialize Supabase client: {e}")

security = HTTPBearer()

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> User:
    """
    Validate the Supabase JWT token and return the authenticated user.
    Uses the Supabase Auth API to verify the token securely.
    """
    if not supabase:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Supabase client not initialized. Check environment variables."
        )

    token = credentials.credentials
    try:
        response = supabase.auth.get_user(token)
        if not response or not response.user:
            raise ValueError("No user found")
        
        user = response.user
        
        # Auto-create profile if missing (Fallback for missing Supabase trigger)
        try:
            profile_check = await anyio.to_thread.run_sync(
                lambda: supabase.table("profiles").select("id").eq("id", user.id).execute()
            )
            if not profile_check.data:
                await anyio.to_thread.run_sync(
                    lambda: supabase.table("profiles").upsert({
                        "id": user.id,
                        "email": user.email,
                        "role": "viewer"
                    }).execute()
                )
        except Exception as e:
            print(f"Warning: Failed to auto-create profile for {user.id}: {e}")

        return user
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

async def require_role(allowed_roles: list[str], credentials: HTTPAuthorizationCredentials = Depends(security)) -> User:
    """
    Dependency for Role-Based Access Control enforcing specific roles.
    Fetches the role directly from the 'profiles' table for accuracy.
    """
    if not supabase:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Supabase client not initialized."
        )

    token = credentials.credentials
    try:
        # Get the authenticated user
        response = supabase.auth.get_user(token)
        if not response or not response.user:
            raise ValueError("Invalid session")
        
        user = response.user
        
        # Fetch role from public.profiles
        profile_res = await anyio.to_thread.run_sync(
            lambda: supabase.table("profiles").select("role").eq("id", user.id).single().execute()
        )
        user_role = profile_res.data.get("role") if profile_res.data else "employee"
        user_role = user_role.lower() # Case-insensitive check

        if user_role not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Access denied. Required roles: {', '.join(allowed_roles)}"
            )
        
        return user
    except Exception as e:
        if isinstance(e, HTTPException):
            raise e
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication failed"
        )

async def require_admin(user: User = Depends(lambda creds=Depends(security): require_role(['admin'], creds))):
    return user

async def require_admin_or_manager(user: User = Depends(lambda creds=Depends(security): require_role(['admin', 'manager'], creds))):
    return user
