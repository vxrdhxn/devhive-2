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
            
        # 1. Detect "Global" queries to increase search depth
        # If user asks for a summary of everything, we need more than 5 chunks
        is_global = any(word in query.lower() for word in ["summarize all", "all files", "everything", "all documents", "total overview"])
        actual_top_k = 40 if is_global else top_k

        # 2. Generate query embedding
        query_vector = await embedding_service.generate_embedding(query)
        
        # 3. Perform similarity search using the match_chunks RPC
        try:
            response = supabase.rpc(
                'match_chunks',
                {
                    'query_embedding': query_vector,
                    'match_threshold': min_similarity,
                    'match_count': actual_top_k,
                    'requesting_user_id': user_id
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
            return []
            
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
