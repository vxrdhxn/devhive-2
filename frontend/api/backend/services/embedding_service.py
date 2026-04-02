from typing import List
import asyncio
from backend.config import get_settings

try:
    from huggingface_hub import AsyncInferenceClient
except ImportError:
    pass

settings = get_settings()

class EmbeddingService:
    """Service for generating vector embeddings using official HuggingFace Inference Client"""
    
    def __init__(self):
        self._client = None
        if settings.huggingface_api_key:
            self._client = AsyncInferenceClient(
                model=settings.embedding_model,
                token=settings.huggingface_api_key
            )

    async def generate_embedding(self, text: str) -> List[float]:
        """Generate an embedding for a piece of text using HF API"""
        if not self._client:
            raise ValueError("Hugging Face client is not initialized")
            
        embeddings = await self._client.feature_extraction(text)
        # Convert numpy array to list if needed
        return embeddings[0] if isinstance(embeddings, list) else embeddings.tolist()[0]

    async def batch_generate_embeddings(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings for a list of text chunks with robust retries"""
        if not self._client:
            raise ValueError("Hugging Face client is not initialized")
            
        embeddings = []
        chunk_size = settings.embedding_batch_size
        
        for i in range(0, len(texts), chunk_size):
            batch = texts[i:i + chunk_size]
            max_retries = 3
            
            for attempt in range(max_retries):
                try:
                    result = await self._client.feature_extraction(batch)
                    batch_embeddings = result if isinstance(result, list) else result.tolist()
                    embeddings.extend(batch_embeddings)
                    break
                except Exception as e:
                    error_str = str(e).lower()
                    if ("503" in error_str or "429" in error_str) and attempt < max_retries - 1:
                        await asyncio.sleep(2 ** attempt)  # Exponential backoff
                        continue
                    raise e
                    
            if i + chunk_size < len(texts):
                await asyncio.sleep(0.5)

        return embeddings

# Singleton instance
embedding_service = EmbeddingService()
