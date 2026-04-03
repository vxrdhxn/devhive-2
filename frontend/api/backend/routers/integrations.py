from fastapi import APIRouter, Depends, HTTPException, status
from typing import List, Dict, Any
from backend.auth.dependencies import get_current_user, User, supabase
from backend.services.integrations.manager import integration_manager
from datetime import datetime

router = APIRouter(prefix="/integrations", tags=["integrations"])

@router.post("/{integration_id}/sync")
async def sync_integration(
    integration_id: str,
    current_user: User = Depends(get_current_user)
):
    """
    Trigger a manual sync for a specific integration.
    Restricted to: Owner OR Admin/Manager.
    """
    if not supabase:
        raise HTTPException(status_code=500, detail="Supabase client not initialized")
        
    print(f"DEBUG: Sync requested for {integration_id} by user {current_user.id}")

    # 1. Fetch integration and user role
    res = supabase.table("integrations").select("*").eq("id", integration_id).single().execute()
    if not res.data:
        raise HTTPException(status_code=404, detail="Integration not found")
        
    integration = res.data
    
    profile_res = await anyio.to_thread.run_sync(
        lambda: supabase.table("profiles").select("role").eq("id", current_user.id).single().execute()
    )
    user_role = profile_res.data.get("role") if profile_res.data else "employee"

    # 2. Enforce RBAC
    is_owner = integration.get("user_id") == current_user.id
    is_privileged = user_role in ["admin", "manager"]

    if not (is_owner or is_privileged):
        raise HTTPException(
            status_code=403, 
            detail="Access denied. Only the owner or an administrator can sync this bridge."
        )

    api_token = integration.get("api_token")
    platform_type = integration.get("platform_type", "notion")
    base_url = integration.get("base_url")
    
    if not api_token:
        raise HTTPException(status_code=400, detail="Integration is missing API token")
        
    try:
        # 3. Update status to syncing
        supabase.table("integrations").update({"status": "syncing"}).eq("id", integration_id).execute()
        
        # 4. Dispatch to adapter
        adapter = integration_manager.get_adapter(platform_type)
        sync_result = await adapter.sync(
            integration_id=integration_id,
            api_token=api_token,
            base_url=base_url
        )
        
        # 5. Update last_synced_at and status
        supabase.table("integrations").update({
            "status": "active",
            "last_synced_at": datetime.utcnow().isoformat()
        }).eq("id", integration_id).execute()
        
        return sync_result
        
    except Exception as e:
        # Revert status to error
        supabase.table("integrations").update({"status": "error"}).eq("id", integration_id).execute()
        raise HTTPException(status_code=500, detail=f"Sync failed: {str(e)}")

@router.get("/")
async def get_integrations(current_user: User = Depends(get_current_user)):
    """List all integrations (shared workspace)."""
    if not supabase:
        return []
    # All users can see active bridges in the shared workspace
    res = supabase.table("integrations").select("*").execute()
    return res.data or []

@router.delete("/{integration_id}")
async def delete_integration(
    integration_id: str,
    current_user: User = Depends(get_current_user)
):
    """
    Remove an integration connection.
    Restricted to: Owner OR Admin/Manager.
    """
    if not supabase:
        raise HTTPException(status_code=500, detail="Supabase client not initialized")
        
    try:
        # 1. Fetch integration and user role
        res = supabase.table("integrations").select("user_id").eq("id", integration_id).single().execute()
        if not res.data:
            raise HTTPException(status_code=404, detail="Integration not found")
        
        profile_res = await anyio.to_thread.run_sync(
            lambda: supabase.table("profiles").select("role").eq("id", current_user.id).single().execute()
        )
        user_role = profile_res.data.get("role") if profile_res.data else "employee"

        # 2. Enforce RBAC
        is_owner = res.data["user_id"] == current_user.id
        is_privileged = user_role in ["admin", "manager"]

        if not (is_owner or is_privileged):
            raise HTTPException(status_code=403, detail="Not authorized to delete this integration")

        supabase.table("integrations").delete().eq("id", integration_id).execute()
        return {"message": "Integration removed successfully"}
    except Exception as e:
        if isinstance(e, HTTPException): raise e
        raise HTTPException(status_code=500, detail=f"Failed to remove integration: {str(e)}")
    except Exception as e:
        if isinstance(e, HTTPException): raise e
        raise HTTPException(status_code=500, detail=f"Failed to remove integration: {str(e)}")
