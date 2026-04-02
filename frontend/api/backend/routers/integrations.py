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
    """
    if not supabase:
        raise HTTPException(status_code=500, detail="Supabase client not initialized")
        
    # 1. Fetch integration details
    print(f"DEBUG: Sync requested for {integration_id} by user {current_user.id}")
    res = supabase.table("integrations")\
        .select("*")\
        .eq("id", integration_id)\
        .eq("user_id", current_user.id)\
        .single()\
        .execute()
        
    if not res.data:
        print(f"DEBUG: No integration found for ID {integration_id} and user {current_user.id}")
        raise HTTPException(status_code=404, detail="Integration not found")
        
    integration = res.data
    api_token = integration.get("api_token")
    platform_type = integration.get("platform_type", "notion")
    base_url = integration.get("base_url")
    
    if not api_token:
        raise HTTPException(status_code=400, detail="Integration is missing API token")
        
    try:
        # 2. Update status to syncing
        supabase.table("integrations").update({"status": "syncing"}).eq("id", integration_id).execute()
        
        # 3. Dispatch to adapter
        adapter = integration_manager.get_adapter(platform_type)
        sync_result = await adapter.sync(
            integration_id=integration_id,
            api_token=api_token,
            base_url=base_url
        )
        
        # 4. Update last_synced_at and status
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
    """List all integrations for the current user."""
    if not supabase:
        return []
    res = supabase.table("integrations").select("*").eq("user_id", current_user.id).execute()
    return res.data or []

@router.delete("/{integration_id}")
async def delete_integration(
    integration_id: str,
    current_user: User = Depends(get_current_user)
):
    """
    Remove an integration connection.
    """
    if not supabase:
        raise HTTPException(status_code=500, detail="Supabase client not initialized")
        
    try:
        response = supabase.table("integrations").delete().eq("id", integration_id).eq("user_id", current_user.id).execute()
        return {"message": "Integration removed successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to remove integration: {str(e)}")
