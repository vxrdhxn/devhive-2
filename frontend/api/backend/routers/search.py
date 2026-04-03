from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
from backend.auth.dependencies import get_current_user
try:
    from gotrue import User
except ImportError:
    from gotrue.types import User
from backend.services.search_engine import search_engine
from backend.services.ai_generator import ai_generator
from backend.auth.dependencies import supabase

router = APIRouter(prefix="/search", tags=["search"])

class SearchRequest(BaseModel):
    query: str
    top_k: int = 5
    min_similarity: float = 0.3
    use_ai: bool = True

class SearchResponse(BaseModel):
    query: str
    ai_answer: Optional[str] = None
    sources: List[str] = []
    chunks: List[Dict[str, Any]]
    confidence: Optional[float] = None

@router.post("", response_model=SearchResponse)
async def perform_search(
    request: SearchRequest,
    current_user: User = Depends(get_current_user)
):
    """
    Perform a semantic search for context and optionally generate an AI answer.
    """
    if not request.query.strip():
        raise HTTPException(status_code=400, detail="Query cannot be empty")

    try:
        # 1. Semantic Search using pgvector
        print(f"DEBUG: Performing semantic search for query: {request.query}")
        matched_chunks = await search_engine.search(
            query=request.query,
            user_id=current_user.id,
            top_k=request.top_k,
            min_similarity=request.min_similarity
        )
        print(f"DEBUG: Found {len(matched_chunks)} matched chunks")

        ai_answer = None
        sources = []
        confidence = None

        # 2. Generative AI using Groq (if requested)
        if request.use_ai:
            if not matched_chunks:
                ai_answer = "I could not find any relevant information in your uploaded documents."
            else:
                # We need to map the output of the search engine correctly to the expected input of the ai_generator
                # The search engine returns dicts with 'id', 'text', 'document_id', 'similarity'
                # The Kiro AI generator expects format like {'filename': ..., 'index': ..., 'text': ...}
                
                # Fetch filenames if search_engine doesn't include it
                # My revised search_engine doesn't fetch filenames, so let's quickly lookup filenames
                # or we just get them here
                doc_ids = list(set([str(c['document_id']) for c in matched_chunks]))
                filenames = {}
                if doc_ids and supabase:
                    try:
                        docs_resp = supabase.table("documents").select("id, filename").in_("id", doc_ids).execute()
                        if docs_resp and docs_resp.data:
                            filenames = {str(d['id']): d['filename'] for d in docs_resp.data}
                        print(f"DEBUG: Found {len(filenames)} filenames for chunks")
                    except Exception as e:
                        print(f"DEBUG: Error fetching filenames from Supabase: {e}")
                        # Continue anyway without filenames
                
                context_chunks = []
                for i, chunk in enumerate(matched_chunks):
                    context_chunks.append({
                        'filename': filenames.get(str(chunk['document_id']), "Unknown Document"),
                        'index': i,
                        'text': chunk['text']
                    })
                    
                ai_result = await ai_generator.generate_answer(request.query, context_chunks)
                ai_answer = ai_result.get("answer")
                sources = ai_result.get("sources", [])
                confidence = ai_result.get("confidence")

        # 3. Log the query
        if supabase:
            try:
                supabase.table("query_logs").insert({
                    "user_id": current_user.id,
                    "query": request.query,
                    "response": ai_answer,
                    "confidence": confidence
                }).execute()
            except Exception as e:
                print(f"Failed to log query: {e}")

        return SearchResponse(**{
            "query": request.query,
            "ai_answer": ai_answer,
            "sources": sources,
            "chunks": matched_chunks,
            "confidence": confidence
        })
        
    except Exception as e:
        import traceback
        error_trace = traceback.format_exc()
        print(f"ERROR: Search endpoint failed: {str(e)}\n{error_trace}")
        raise HTTPException(status_code=500, detail=f"Search failed: {str(e)}")
