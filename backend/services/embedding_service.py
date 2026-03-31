from typing import List
import anyio
import os
from backend.config import get_settings

settings = get_settings()

class EmbeddingService:
    """Service for generating vector embeddings using SentenceTransformer"""
    
    def __init__(self):
        self._model = None
        
    def _get_model(self):
        """Internal helper to load model synchronously in a thread"""
        if self._model is None:
            from sentence_transformers import SentenceTransformer
            
            # Define a local cache directory in the project root (matching pre_download.py)
            base_dir = os.path.dirname(os.path.abspath(__file__))
            cache_folder = os.path.join(os.path.dirname(base_dir), ".model_cache")
            
            print(f"DEBUG: Initializing SentenceTransformer model: {settings.embedding_model}")
            print(f"DEBUG: Using local cache folder: {cache_folder}")
            
            self._model = SentenceTransformer(
                settings.embedding_model, 
                cache_folder=cache_folder
            )
        return self._model

    async def generate_embedding(self, text: str) -> List[float]:
        """Generate an embedding for a piece of text (Non-blocking)"""
        def _sync_generate():
            model = self._get_model()
            return model.encode(text).tolist()
            
        return await anyio.to_thread.run_sync(_sync_generate)

    async def batch_generate_embeddings(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings for a list of text chunks (Non-blocking)"""
        def _sync_batch_generate():
            model = self._get_model()
            embeddings = model.encode(
                texts, 
                batch_size=settings.embedding_batch_size,
                show_progress_bar=False
            )
            return embeddings.tolist()
            
        return await anyio.to_thread.run_sync(_sync_batch_generate)

# Singleton instance
embedding_service = EmbeddingService()
