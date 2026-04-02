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
            user_id=current_user.id
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
    List all documents uploaded by the current user.
    """
    if not supabase:
        raise HTTPException(status_code=500, detail="Supabase not configured")

    # The RLS policies will automatically scope this to the current user's documents
    # However we explicitly filter by uploaded_by for extra safety if service-role is used
    response = await anyio.to_thread.run_sync(
        lambda: supabase.table("documents").select("*").eq("uploaded_by", current_user.id).order('created_at', desc=True).execute()
    )
    return response.data

@router.delete("/{document_id}")
async def delete_document(document_id: str, current_user: User = Depends(get_current_user)):
    """
    Delete a document and its associated chunks from the vector store.
    """
    if not supabase:
        raise HTTPException(status_code=500, detail="Supabase not configured")

    try:
        response = await anyio.to_thread.run_sync(
            lambda: supabase.table("documents").delete().eq("id", document_id).eq("uploaded_by", current_user.id).execute()
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Delete failed: {str(e)}")
        
    return {"message": "Document deleted successfully"}
