from flask import Blueprint, jsonify
from utils.pinecone_utils import index
from utils.openai_utils import client

health_bp = Blueprint('health', __name__)

@health_bp.route("/health", methods=["GET"])
def health_check():
    """Health check endpoint for deployment monitoring"""
    try:
        # Check Pinecone connection
        index_stats = index.describe_index_stats()
        
        # Check OpenAI connection (simple test)
        test_response = client.models.list()
        
        return jsonify({
            "status": "healthy",
            "services": {
                "pinecone": "connected",
                "openai": "connected"
            },
            "index_stats": {
                "total_vector_count": index_stats.total_vector_count,
                "dimension": index_stats.dimension
            },
            "timestamp": "2024-01-01T00:00:00Z"
        })
    except Exception as e:
        return jsonify({
            "status": "unhealthy",
            "error": str(e)
        }), 500 