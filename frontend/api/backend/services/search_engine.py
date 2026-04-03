from typing import List, Dict, Any
from backend.services.embedding_service import embedding_service
from backend.auth.dependencies import supabase

class SearchEngine:
    """Service for performing semantic searches using Supabase pgvector RPC"""
    
    @staticmethod
    async def search(
        query: str, 
        user_id: str, 
        top_k: int = 5,
        min_similarity: float = 0.3
    ) -> List[Dict[str, Any]]:
        """Perform a semantic search against the vector database using Supabase RPC"""
        if not supabase:
            raise ValueError("Supabase client is not initialized.")
            
        # 1. Generate query embedding
        query_vector = await embedding_service.generate_embedding(query)
        
        # 2. Perform similarity search using the match_chunks RPC
        # The RPC is role-aware: Admin/Manager sees all, Employee sees public + own
        try:
            response = supabase.rpc(
                'match_chunks',
                {
                    'query_embedding': query_vector,
                    'match_threshold': min_similarity,
                    'match_count': top_k,
                    'requesting_user_id': user_id # Using clear parameter name for the new SQL function
                }
            ).execute()
        except Exception as e:
            print(f"ERROR: Supabase RPC call failed: {e}")
            raise ValueError(f"Vector search RPC failed: {str(e)}")

        if hasattr(response, 'error') and response.error:
            print(f"ERROR: PostgREST error in match_chunks: {response.error}")
            raise ValueError(f"Database error during vector search: {response.error.get('message', 'Unknown error')}")

        results = response.data
        if results is None:
            print("DEBUG: match_chunks RPC returned None data")
            return []
            
        print(f"DEBUG: match_chunks RPC returned {len(results)} results")
        return [
            {
                "id": str(r['chunk_id']),
                "text": r['content'],
                "document_id": str(r['document_id']),
                "similarity": float(r['similarity'])
            } for r in results
        ]

# Singleton instance
search_engine = SearchEngine()
