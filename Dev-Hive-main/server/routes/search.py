from flask import Blueprint, request, jsonify
import logging
from utils.openai_utils import get_embedding
from utils.pinecone_utils import query_chunks, check_index_health
from utils.activity_tracker import log_search_activity

search_bp = Blueprint('search', __name__)
logger = logging.getLogger(__name__)

@search_bp.route("/search", methods=["POST"])
def search():
    data = request.json
    query = data.get("query", "")
    top_k = data.get("top_k", 5)
    metadata_filter = data.get("filter", None)

    if not query:
        return jsonify({"error": "Missing query parameter"}), 400

    try:
        # First check if Pinecone index is healthy
        if not check_index_health():
            return jsonify({
                "error": "Pinecone index is currently unavailable. Please try again later.",
                "details": "The vector database is experiencing connectivity issues."
            }), 503

        # Get embedding for the search query
        logger.info(f"Getting embedding for query: {query[:50]}...")
        query_embedding = get_embedding(query)
        
        # Search for similar chunks with retry logic
        logger.info(f"Searching for {top_k} results...")
        results = query_chunks(query_embedding, top_k=top_k, metadata_filter=metadata_filter)
        
        # Format results
        formatted_results = []
        for match in results.matches:
            formatted_results.append({
                "id": match.id,
                "score": match.score,
                "text": match.metadata.get("text", ""),
                "source": match.metadata.get("source", ""),
                "type": match.metadata.get("type", ""),
                "chunk_index": match.metadata.get("chunk_index", 0),
                "timestamp": match.metadata.get("timestamp", "")
            })
        
        logger.info(f"Search completed successfully with {len(formatted_results)} results")
        
        # Log search activity
        log_search_activity(query, len(formatted_results))
        
        return jsonify({
            "status": "success",
            "query": query,
            "results": formatted_results,
            "total_results": len(formatted_results)
        })
        
    except Exception as e:
        error_msg = str(e)
        logger.error(f"Search failed: {error_msg}")
        
        # Provide specific error messages for common issues
        if "too many" in error_msg.lower() or "rate limit" in error_msg.lower():
            return jsonify({
                "error": "Search rate limit exceeded. Please wait a moment and try again.",
                "details": "Too many requests to the vector database. Please slow down your search requests."
            }), 429
        elif "500" in error_msg or "internal server error" in error_msg.lower():
            return jsonify({
                "error": "Vector database service temporarily unavailable.",
                "details": "The search service is experiencing issues. Please try again in a few minutes."
            }), 503
        elif "connection" in error_msg.lower() or "timeout" in error_msg.lower():
            return jsonify({
                "error": "Unable to connect to search service.",
                "details": "Network connectivity issues with the vector database."
            }), 503
        else:
            return jsonify({
                "error": f"Search failed: {error_msg}",
                "details": "An unexpected error occurred during the search operation."
            }), 500
