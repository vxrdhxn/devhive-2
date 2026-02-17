import re
import hashlib
import uuid
from typing import List, Dict, Any
from datetime import datetime

def generate_content_hash(content: str) -> str:
    """Generate a hash for content to detect duplicates"""
    # Normalize content (remove extra whitespace, lowercase)
    normalized = re.sub(r'\s+', ' ', content.strip().lower())
    return hashlib.md5(normalized.encode()).hexdigest()

def chunk_text(text: str, max_tokens: int = 300, overlap: int = 50) -> List[Dict[str, Any]]:
    """
    Enhanced chunking with metadata and deduplication support
    
    Args:
        text: Text to chunk
        max_tokens: Maximum tokens per chunk
        overlap: Overlap between chunks in characters
    
    Returns:
        List of chunk dictionaries with metadata
    """
    if not text or not text.strip():
        return []
    
    # Clean and normalize text
    text = re.sub(r'\s+', ' ', text.strip())
    
    # Split into sentences/paragraphs
    sentences = re.split(r'\n{2,}|\.\s+', text)
    
    chunks = []
    current_chunk = ""
    chunk_start = 0
    
    for i, sentence in enumerate(sentences):
        sentence = sentence.strip()
        if not sentence:
            continue
            
        # Check if adding this sentence would exceed max_tokens
        estimated_tokens = len(current_chunk + sentence) // 4  # rough estimate
        
        if estimated_tokens > max_tokens and current_chunk:
            # Finalize current chunk
            chunk_data = {
                "id": str(uuid.uuid4()),
                "text": current_chunk.strip(),
                "content_hash": generate_content_hash(current_chunk.strip()),
                "start_pos": chunk_start,
                "end_pos": chunk_start + len(current_chunk),
                "sentence_count": len([s for s in current_chunk.split('.') if s.strip()]),
                "word_count": len(current_chunk.split()),
                "chunk_index": len(chunks)
            }
            chunks.append(chunk_data)
            
            # Start new chunk with overlap
            overlap_text = current_chunk[-overlap:] if overlap > 0 else ""
            current_chunk = overlap_text + " " + sentence
            chunk_start = chunk_start + len(current_chunk) - len(overlap_text) - len(sentence)
        else:
            current_chunk += " " + sentence if current_chunk else sentence
    
    # Add final chunk
    if current_chunk.strip():
        chunk_data = {
            "id": str(uuid.uuid4()),
            "text": current_chunk.strip(),
            "content_hash": generate_content_hash(current_chunk.strip()),
            "start_pos": chunk_start,
            "end_pos": chunk_start + len(current_chunk),
            "sentence_count": len([s for s in current_chunk.split('.') if s.strip()]),
            "word_count": len(current_chunk.split()),
            "chunk_index": len(chunks)
        }
        chunks.append(chunk_data)
    
    return chunks

def deduplicate_chunks(chunks: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Remove duplicate chunks based on content hash
    
    Args:
        chunks: List of chunk dictionaries
    
    Returns:
        Deduplicated list of chunks
    """
    seen_hashes = set()
    unique_chunks = []
    
    for chunk in chunks:
        content_hash = chunk.get("content_hash")
        if content_hash and content_hash not in seen_hashes:
            seen_hashes.add(content_hash)
            unique_chunks.append(chunk)
    
    return unique_chunks

def merge_chunks_from_sources(source_chunks: Dict[str, List[Dict[str, Any]]]) -> List[Dict[str, Any]]:
    """
    Merge chunks from multiple sources and deduplicate
    
    Args:
        source_chunks: Dictionary with source names as keys and chunk lists as values
    
    Returns:
        Merged and deduplicated chunks
    """
    all_chunks = []
    
    for source_name, chunks in source_chunks.items():
        for chunk in chunks:
            # Add source information to chunk metadata
            chunk["source_name"] = source_name
            chunk["integration_timestamp"] = datetime.now().isoformat()
            all_chunks.append(chunk)
    
    # Deduplicate based on content hash
    unique_chunks = deduplicate_chunks(all_chunks)
    
    # Sort by source priority (GitHub > Notion > Slack) and then by chunk index
    source_priority = {"github": 1, "notion": 2, "slack": 3}
    
    def sort_key(chunk):
        source = chunk.get("source_name", "").lower()
        priority = source_priority.get(source, 999)
        chunk_index = chunk.get("chunk_index", 0)
        return (priority, chunk_index)
    
    unique_chunks.sort(key=sort_key)
    
    return unique_chunks

def create_pinecone_vectors(chunks: List[Dict[str, Any]], source_info: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Create Pinecone vectors from chunks with enhanced metadata
    
    Args:
        chunks: List of chunk dictionaries
        source_info: Source information (title, source, type, etc.)
    
    Returns:
        List of Pinecone vector dictionaries
    """
    vectors = []
    
    for chunk in chunks:
        vector_data = {
            "id": chunk["id"],
            "values": None,  # Will be filled with embedding
            "metadata": {
                "text": chunk["text"],
                "content_hash": chunk["content_hash"],
                "title": source_info.get("title", ""),
                "source": source_info.get("source", ""),
                "type": source_info.get("type", ""),
                "integration": source_info.get("integration", ""),
                "source_name": chunk.get("source_name", ""),
                "chunk_index": chunk.get("chunk_index", 0),
                "sentence_count": chunk.get("sentence_count", 0),
                "word_count": chunk.get("word_count", 0),
                "start_pos": chunk.get("start_pos", 0),
                "end_pos": chunk.get("end_pos", 0),
                "integration_timestamp": chunk.get("integration_timestamp", ""),
                "timestamp": datetime.now().isoformat()
            }
        }
        vectors.append(vector_data)
    
    return vectors

def process_integration_data(data_items: List[Dict[str, Any]], integration_type: str) -> List[Dict[str, Any]]:
    """
    Process integration data with enhanced chunking and deduplication
    
    Args:
        data_items: List of data items from integration
        integration_type: Type of integration (github, notion, slack)
    
    Returns:
        List of processed chunks ready for Pinecone
    """
    all_chunks = []
    
    for item in data_items:
        content = item.get("content", "")
        if not content or len(content.strip()) < 10:  # Skip very short content
            continue
        
        # Create source info
        source_info = {
            "title": item.get("title", ""),
            "source": item.get("source", ""),
            "type": item.get("type", ""),
            "integration": integration_type
        }
        
        # Chunk the content
        chunks = chunk_text(content, max_tokens=300, overlap=50)
        
        # Add source information to chunks
        for chunk in chunks:
            chunk["source_name"] = integration_type
            chunk["source_info"] = source_info
        
        all_chunks.extend(chunks)
    
    # Deduplicate chunks
    unique_chunks = deduplicate_chunks(all_chunks)
    
    return unique_chunks 