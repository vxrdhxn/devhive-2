from typing import List
import httpx
from backend.config import get_settings

settings = get_settings()

class EmbeddingService:
    """Service for generating vector embeddings using HuggingFace Inference API"""
    
    def __init__(self):
        self._api_url = f"https://api-inference.huggingface.co/pipeline/feature-extraction/{settings.embedding_model}"
        self._headers = {}
        if settings.huggingface_api_key:
            self._headers["Authorization"] = f"Bearer {settings.huggingface_api_key}"

    async def generate_embedding(self, text: str) -> List[float]:
        """Generate an embedding for a piece of text using HF API"""
        async with httpx.AsyncClient() as client:
            response = await client.post(
                self._api_url, 
                headers=self._headers, 
                json={"inputs": [text], "options": {"wait_for_model": True}}
            )
            response.raise_for_status()
            data = response.json()
            # HF feature-extraction returns a list of embeddings for the input texts
            return data[0]

    async def batch_generate_embeddings(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings for a list of text chunks with robust retries"""
        import asyncio
        embeddings = []
        
        # We can chunk the requests if batch_size is defined, 
        # but for HF API we will just send it as an array to the endpoint.
        # It's better to chunk them locally to avoid huge payload limits.
        chunk_size = settings.embedding_batch_size
        async with httpx.AsyncClient(timeout=httpx.Timeout(60.0)) as client:
            for i in range(0, len(texts), chunk_size):
                batch = texts[i:i + chunk_size]
                
                max_retries = 3
                for attempt in range(max_retries):
                    try:
                        response = await client.post(
                            self._api_url,
                            headers=self._headers,
                            json={"inputs": batch, "options": {"wait_for_model": True}}
                        )
                        response.raise_for_status()
                        data = response.json()
                        embeddings.extend(data)
                        break
                    except httpx.HTTPStatusError as e:
                        if e.response.status_code in [503, 429] and attempt < max_retries - 1:
                            await asyncio.sleep(2 ** attempt) # Exponential backoff
                            continue
                        raise e
                
                # Small delay to keep Hugging Face rate limits happy
                if i + chunk_size < len(texts):
                    await asyncio.sleep(0.5)
                
        return embeddings

# Singleton instance
embedding_service = EmbeddingService()
