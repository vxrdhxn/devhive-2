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
        response = supabase.rpc(
            'match_chunks',
            {
                'query_embedding': query_vector,
                'match_threshold': min_similarity,
                'match_count': top_k,
                'user_id': user_id
            }
        ).execute()

        results = response.data
        if not results:
            print("DEBUG: No chunks returned from match_chunks RPC")
            return []
            
        print(f"DEBUG: match_chunks RPC returned {len(results)} results")
        return [
            {
                "id": str(r['id']),
                "text": r['content'],
                "document_id": str(r['document_id']),
                "similarity": float(r['similarity'])
            } for r in results
        ]

# Singleton instance
search_engine = SearchEngine()
