import os
import sys
import anyio
# Ensure the project root is in sys.path for internal imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fastapi import APIRouter, Depends, File, UploadFile, HTTPException, BackgroundTasks
from backend.auth.dependencies import get_current_user, supabase
try:
    from gotrue import User
except ImportError:
    from gotrue.types import User
from backend.services.ingestion_service import ingestion_service

router = APIRouter(prefix="/documents", tags=["documents"])

@router.post("/upload")
async def upload_document(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    is_private: bool = False,
    current_user: User = Depends(get_current_user)
):
    """
    Upload a document for processing and vector ingestion.
    Runs the heavy embedding process in the background.
    """
    print(f"DEBUG: Received upload request for {file.filename} (content_type: {file.content_type})")
    
    if not file.filename:
        print("DEBUG: Upload failed - No filename")
        raise HTTPException(status_code=400, detail="No file selected")

    try:
        content = await file.read()
        print(f"DEBUG: Successfully read {len(content)} bytes from {file.filename}")
    except Exception as e:
        print(f"DEBUG: Upload failed during file read: {e}")
        raise HTTPException(status_code=400, detail=f"Could not read file contents: {str(e)}")
        
    print(f"DEBUG: Starting ingestion for {file.filename}")
    try:
        # Await the process before returning so Vercel Serverless does not freeze the context
        result = await ingestion_service.process_and_store_document(
            file_content=content,
            filename=file.filename,
            file_type=file.content_type or "text/plain",
            user_id=current_user.id,
            is_private=is_private
        )
        print(f"DEBUG: Ingestion SUCCEEDED for {file.filename}")
    except Exception as e:
        print(f"DEBUG: Task failed for document {file.filename}: {e}")
        raise HTTPException(status_code=500, detail=f"Ingestion failed: {str(e)}")

    print(f"DEBUG: Returning success for upload of {file.filename}")
    return {"message": "Document processed and inserted successfully", "filename": file.filename}

@router.get("/")
async def get_documents(current_user: User = Depends(get_current_user)):
    """
    List all documents. Scoped by role:
    - Admin/Manager: All documents
    - Employee: Only public documents + their own uploads
    """
    if not supabase:
        raise HTTPException(status_code=500, detail="Supabase not configured")

    # 1. Fetch user role
    profile_res = await anyio.to_thread.run_sync(
        lambda: supabase.table("profiles").select("role").eq("id", current_user.id).single().execute()
    )
    user_role = profile_res.data.get("role") if profile_res.data else "employee"

    # 2. Build Query
    query = supabase.table("documents").select("*")
    
    if user_role not in ["admin", "manager"]:
        # Show public documents OR documents they personally uploaded
        query = query.or_(f"is_private.eq.false,uploaded_by.eq.{current_user.id}")
    
    response = await anyio.to_thread.run_sync(
        lambda: query.order('created_at', desc=True).execute()
    )
    return response.data

@router.delete("/{document_id}")
async def delete_document(document_id: str, current_user: User = Depends(get_current_user)):
    """
    Delete a document. 
    Restricted to: Document Owner OR Admin/Manager.
    """
    if not supabase:
        raise HTTPException(status_code=500, detail="Supabase not configured")

    # 1. Fetch document ownership and user role
    try:
        # Fetch document
        doc_res = await anyio.to_thread.run_sync(
            lambda: supabase.table("documents").select("uploaded_by").eq("id", document_id).single().execute()
        )
        if not doc_res.data:
            raise HTTPException(status_code=404, detail="Document not found")
        
        doc_owner = doc_res.data.get("uploaded_by")

        # Fetch user role
        profile_res = await anyio.to_thread.run_sync(
            lambda: supabase.table("profiles").select("role").eq("id", current_user.id).single().execute()
        )
        user_role = profile_res.data.get("role") if profile_res.data else "employee"

        # 2. Enforce RBAC
        is_owner = str(doc_owner) == str(current_user.id)
        is_privileged = user_role in ["admin", "manager"]

        if not (is_owner or is_privileged):
            print(f"DEBUG: ACCESS DENIED for delete {document_id} by user {current_user.id} (Role: {user_role})")
            raise HTTPException(
                status_code=403, 
                detail="Not authorized to delete this document. Ownership or Admin/Manager role required."
            )

        print(f"DEBUG: DELETE AUTHORIZED for {document_id} by user {current_user.id}")

        # 3. Execute delete
        response = await anyio.to_thread.run_sync(
            lambda: supabase.table("documents").delete().eq("id", document_id).execute()
        )
        
        if not response.data or len(response.data) == 0:
            raise HTTPException(status_code=404, detail="Document not found or already deleted")
            
        print(f"DEBUG: Successfully deleted document {document_id}")
    except Exception as e:
        if isinstance(e, HTTPException): raise e
        print(f"ERROR: Database Delete Failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Database Delete Failed: {str(e)}")
        
    return {"message": "Document deleted successfully"}
