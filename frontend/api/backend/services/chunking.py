# pyre-ignore-all-errors
from typing import List
import re

class ChunkingService:
    """Service for splitting text into smaller chunks with overlap"""
    
    @staticmethod
    def chunk_text(
        text: str, 
        chunk_size: int = 1000, 
        chunk_overlap: int = 200
    ) -> List[str]:
        if not text or not text.strip():
            return []
            
        chunks: List[str] = []
        text_length = len(text)
        start = 0
        
        while start < text_length:
            # Determine initial end point
            end = min(start + chunk_size, text_length)
            
            # If we aren't at the very end, try to find a natural break (space)
            if end < text_length:
                boundary = text.rfind(" ", start, end)
                # Ensure boundary is after start to make progress
                if boundary != -1 and boundary > start:
                    end = boundary
            
            # Extract and add chunk
            chunk = text[start:end].strip()
            if chunk:
                chunks.append(chunk)
            
            # Calculate next start point with overlap
            next_start = end - chunk_overlap
            
            # CRITICAL: Ensure we always make progress and never go backwards
            if next_start <= start:
                start = end
            else:
                start = next_start
                
            # Safety check: if start didn't move forward at all despite not being at end
            if start <= 0 and text_length > 0 and len(chunks) > 0:
                # This handles edge cases where chunk_size might be too small
                start = end
        
        return [c for c in chunks if c.strip()]

# Singleton instance
chunking_service = ChunkingService()
