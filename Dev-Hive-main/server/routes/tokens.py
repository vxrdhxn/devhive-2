from flask import Blueprint, request, jsonify
from utils.token_manager import token_manager
import logging

tokens_bp = Blueprint('tokens', __name__)
logger = logging.getLogger(__name__)

@tokens_bp.route("/tokens/store", methods=["POST"])
def store_token():
    """Store a token for a service"""
    try:
        data = request.json
        service = data.get("service")
        token = data.get("token")
        
        if not service or not token:
            return jsonify({"error": "Missing service or token"}), 400
        
        success, message = token_manager.store_token(service, token)
        
        if success:
            return jsonify({
                "status": "success",
                "message": message,
                "service": service
            })
        else:
            return jsonify({"error": message}), 400
            
    except Exception as e:
        logger.error(f"Token storage failed: {e}")
        return jsonify({"error": f"Token storage failed: {str(e)}"}), 500

@tokens_bp.route("/tokens/get/<service>", methods=["GET"])
def get_token(service):
    """Get a stored token for a service"""
    try:
        token = token_manager.get_token(service)
        
        if token:
            return jsonify({
                "status": "success",
                "service": service,
                "has_token": True
            })
        else:
            return jsonify({
                "status": "success",
                "service": service,
                "has_token": False
            })
            
    except Exception as e:
        logger.error(f"Token retrieval failed: {e}")
        return jsonify({"error": f"Token retrieval failed: {str(e)}"}), 500

@tokens_bp.route("/tokens/remove/<service>", methods=["DELETE"])
def remove_token(service):
    """Remove a stored token for a service"""
    try:
        success = token_manager.remove_token(service)
        
        if success:
            return jsonify({
                "status": "success",
                "message": f"Token for {service} removed successfully"
            })
        else:
            return jsonify({"error": f"No token found for {service}"}), 404
            
    except Exception as e:
        logger.error(f"Token removal failed: {e}")
        return jsonify({"error": f"Token removal failed: {str(e)}"}), 500

@tokens_bp.route("/tokens/list", methods=["GET"])
def list_tokens():
    """List all stored tokens (without showing actual tokens)"""
    try:
        tokens = token_manager.list_tokens()
        
        return jsonify({
            "status": "success",
            "tokens": tokens
        })
        
    except Exception as e:
        logger.error(f"Token listing failed: {e}")
        return jsonify({"error": f"Token listing failed: {str(e)}"}), 500

@tokens_bp.route("/tokens/validate", methods=["POST"])
def validate_tokens():
    """Validate all stored tokens"""
    try:
        results = token_manager.validate_stored_tokens()
        
        return jsonify({
            "status": "success",
            "validation_results": results
        })
        
    except Exception as e:
        logger.error(f"Token validation failed: {e}")
        return jsonify({"error": f"Token validation failed: {str(e)}"}), 500 