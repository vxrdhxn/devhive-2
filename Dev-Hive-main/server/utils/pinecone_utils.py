import os
import time
import logging
from pinecone import Pinecone
from dotenv import load_dotenv

load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Pinecone with new API
pc = Pinecone(api_key=os.getenv("PINECONE_API_KEY"))

# Get the index
index_name = os.getenv("PINECONE_INDEX_NAME")
index = pc.Index(index_name)

def upsert_chunks(vectors, max_retries=3, retry_delay=1):
    """Upsert chunks with retry logic"""
    for attempt in range(max_retries):
        try:
            index.upsert(vectors=vectors)
            logger.info(f"Successfully upserted {len(vectors)} vectors")
            return True
        except Exception as e:
            logger.warning(f"Upsert attempt {attempt + 1} failed: {str(e)}")
            if attempt < max_retries - 1:
                time.sleep(retry_delay * (2 ** attempt))  # Exponential backoff
            else:
                logger.error(f"All upsert attempts failed: {str(e)}")
                raise e

def query_chunks(vector, top_k=5, metadata_filter=None, max_retries=3, retry_delay=1):
    """Query chunks with retry logic and rate limiting"""
    for attempt in range(max_retries):
        try:
            # Add a small delay to prevent rate limiting
            if attempt > 0:
                time.sleep(retry_delay * (2 ** attempt))
            
            results = index.query(
                vector=vector,
                top_k=top_k,
                include_metadata=True,
                filter=metadata_filter
            )
            logger.info(f"Successfully queried {len(results.matches)} results")
            return results
            
        except Exception as e:
            error_msg = str(e)
            logger.warning(f"Query attempt {attempt + 1} failed: {error_msg}")
            
            # Check if it's a rate limiting error
            if "too many" in error_msg.lower() or "rate limit" in error_msg.lower():
                wait_time = retry_delay * (2 ** attempt) * 2  # Longer wait for rate limits
                logger.info(f"Rate limit detected, waiting {wait_time} seconds...")
                time.sleep(wait_time)
            elif "500" in error_msg or "internal server error" in error_msg.lower():
                wait_time = retry_delay * (2 ** attempt)
                logger.info(f"Server error detected, waiting {wait_time} seconds...")
                time.sleep(wait_time)
            else:
                # For other errors, don't retry
                logger.error(f"Non-retryable error: {error_msg}")
                raise e
            
            if attempt == max_retries - 1:
                logger.error(f"All query attempts failed: {error_msg}")
                raise e

def check_index_health():
    """Check if the Pinecone index is healthy"""
    try:
        # Try a simple query to test connectivity
        test_vector = [0.0] * 1536  # OpenAI embedding dimension
        results = index.query(vector=test_vector, top_k=1, include_metadata=False)
        return True
    except Exception as e:
        logger.error(f"Index health check failed: {str(e)}")
        return False

def get_index_stats():
    """Get index statistics"""
    try:
        stats = index.describe_index_stats()
        return stats
    except Exception as e:
        logger.error(f"Failed to get index stats: {str(e)}")
        return None
