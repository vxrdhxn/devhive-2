from flask import Blueprint, request, jsonify
from utils.integration_manager import integration_manager
from utils.activity_tracker import log_integration_activity
import os
import datetime

integrations_bp = Blueprint('integrations', __name__)

@integrations_bp.route("/integrate/github", methods=["POST"])
def integrate_github():
    """Integrate GitHub repository data"""
    try:
        data = request.json
        owner = data.get("owner")
        repo = data.get("repo")
        
        if not owner or not repo:
            return jsonify({"error": "Missing owner or repo"}), 400
        
        # Use integration manager
        result = integration_manager.integrate_github(owner, repo)
        
        if result["success"]:
            # Log integration activity
            log_integration_activity("GitHub", result["chunks_stored"], result["duplicates_removed"])
            
            return jsonify({
                "status": "success",
                "source": result["source"],
                "documents_processed": result["documents_processed"],
                "chunks_processed": result["chunks_processed"],
                "chunks_stored": result["chunks_stored"],
                "duplicates_removed": result["duplicates_removed"],
                "integration": "github"
            })
        else:
            return jsonify({"error": result["error"]}), 400
        
    except Exception as e:
        return jsonify({"error": f"GitHub integration failed: {str(e)}"}), 500

@integrations_bp.route("/integrate/notion", methods=["POST"])
def integrate_notion():
    """Integrate Notion data"""
    try:
        data = request.json
        search_query = data.get("search_query", "")
        page_ids = data.get("page_ids", [])
        database_ids = data.get("database_ids", [])
        read_all_workspace = data.get("read_all_workspace", False)
        
        if not search_query and not page_ids and not database_ids and not read_all_workspace:
            return jsonify({"error": "Must provide search_query, page_ids, database_ids, or set read_all_workspace to true"}), 400
        
        # Use integration manager
        result = integration_manager.integrate_notion(
            search_query=search_query,
            page_ids=page_ids if page_ids else None,
            database_ids=database_ids if database_ids else None,
            read_all_workspace=read_all_workspace
        )
        
        if result["success"]:
            # Log integration activity
            log_integration_activity("Notion", result["chunks_stored"], result["duplicates_removed"])
            
            return jsonify({
                "status": "success",
                "source": result["source"],
                "documents_processed": result["documents_processed"],
                "chunks_processed": result["chunks_processed"],
                "chunks_stored": result["chunks_stored"],
                "duplicates_removed": result["duplicates_removed"],
                "integration": "notion"
            })
        else:
            return jsonify({"error": result["error"]}), 400
        
    except Exception as e:
        return jsonify({"error": f"Notion integration failed: {str(e)}"}), 500

@integrations_bp.route("/integrate/slack", methods=["POST"])
def integrate_slack():
    """Integrate Slack channel messages and conversation history"""
    try:
        data = request.json
        channel_ids = data.get("channel_ids", [])
        search_query = data.get("search_query", "")
        include_dms = data.get("include_dms", False)
        
        # Use integration manager
        result = integration_manager.integrate_slack(
            channel_ids=channel_ids if channel_ids else None,
            search_query=search_query if search_query else None,
            include_dms=include_dms
        )
        
        if result["success"]:
            # Log integration activity
            log_integration_activity("Slack", result["chunks_stored"], result["duplicates_removed"])
            
            return jsonify({
                "status": "success",
                "source": result["source"],
                "messages_processed": result["messages_processed"],
                "chunks_processed": result["chunks_processed"],
                "chunks_stored": result["chunks_stored"],
                "duplicates_removed": result["duplicates_removed"],
                "integration": "slack"
            })
        else:
            return jsonify({"error": result["error"]}), 400
        
    except Exception as e:
        return jsonify({"error": f"Slack integration failed: {str(e)}"}), 500

@integrations_bp.route("/integrate/bulk", methods=["POST"])
def integrate_bulk():
    """Bulk integration from multiple sources"""
    try:
        data = request.json
        integrations = data.get("integrations", [])
        
        if not integrations:
            return jsonify({"error": "No integrations specified"}), 400
        
        # Prepare configurations for integration manager
        github_config = None
        notion_config = None
        slack_config = None
        
        for integration in integrations:
            integration_type = integration.get("type")
            
            if integration_type == "github":
                owner = integration.get("owner")
                repo = integration.get("repo")
                if owner and repo:
                    github_config = {"owner": owner, "repo": repo}
            
            elif integration_type == "notion":
                notion_config = {
                    "search_query": integration.get("search_query", ""),
                    "page_ids": integration.get("page_ids", []),
                    "database_ids": integration.get("database_ids", []),
                    "read_all_workspace": integration.get("read_all_workspace", False)
                }
            
            elif integration_type == "slack":
                slack_config = {
                    "channel_ids": integration.get("channel_ids", []),
                    "search_query": integration.get("search_query", ""),
                    "include_dms": integration.get("include_dms", False)
                }
        
        # Use integration manager for comprehensive integration
        result = integration_manager.integrate_all_sources(
            github_config=github_config,
            notion_config=notion_config,
            slack_config=slack_config
        )
        
        if result["success"]:
            return jsonify({
                "status": "success",
                "integrations_processed": len(result["integrations"]),
                "total_chunks_processed": result["total_chunks_processed"],
                "total_chunks_stored": result["total_chunks_stored"],
                "total_duplicates_removed": result["total_duplicates_removed"],
                "sources_integrated": result["sources_integrated"],
                "results": result["integrations"]
            })
        else:
            return jsonify({"error": result["error"]}), 500
        
    except Exception as e:
        return jsonify({"error": f"Bulk integration failed: {str(e)}"}), 500

@integrations_bp.route("/integrate/all", methods=["POST"])
def integrate_all():
    """Integrate all available sources with default configurations"""
    try:
        # Get tokens from token manager instead of environment variables
        from utils.token_manager import token_manager
        
        github_token = token_manager.get_token("github")
        notion_token = token_manager.get_token("notion")
        slack_token = token_manager.get_token("slack")
        
        # Default configurations
        github_config = {"owner": "nannndini", "repo": "KTP"} if github_token else None
        notion_config = {"read_all_workspace": True} if notion_token else None
        slack_config = {
            "channel_ids": [],  # Empty list means all accessible channels
            "search_query": "",  # No specific search query
            "include_dms": False  # Don't include DMs by default
        } if slack_token else None
        
        # Use integration manager
        result = integration_manager.integrate_all_sources(
            github_config=github_config,
            notion_config=notion_config,
            slack_config=slack_config
        )
        
        if result["success"]:
            return jsonify({
                "status": "success",
                "integrations_processed": len(result["integrations"]),
                "total_chunks_processed": result["total_chunks_processed"],
                "total_chunks_stored": result["total_chunks_stored"],
                "total_duplicates_removed": result["total_duplicates_removed"],
                "sources_integrated": result["sources_integrated"],
                "results": result["integrations"]
            })
        else:
            return jsonify({"error": result["error"]}), 500
        
    except Exception as e:
        return jsonify({"error": f"All sources integration failed: {str(e)}"}), 500

@integrations_bp.route("/stats", methods=["GET"])
def get_integration_stats():
    """Get statistics about integrated data"""
    try:
        # Get integration stats
        integration_stats = integration_manager.get_integration_stats()
        
        # Get real Pinecone stats
        from utils.pinecone_utils import get_index_stats, check_index_health
        
        pinecone_stats = {}
        if check_index_health():
            try:
                index_stats = get_index_stats()
                pinecone_stats = {
                    "total_vectors": index_stats.get("total_vector_count", 0),
                    "dimension": index_stats.get("dimension", 0)
                }
            except Exception as e:
                pinecone_stats = {"error": str(e)}
        else:
            pinecone_stats = {"error": "Pinecone not available"}
        
        # Combine stats
        combined_stats = {
            **integration_stats,
            "pinecone_stats": pinecone_stats,
            "total_vectors": pinecone_stats.get("total_vectors", 0)  # Use real Pinecone count
        }
        
        return jsonify({
            "status": "success",
            "stats": combined_stats
        })
    except Exception as e:
        return jsonify({"error": f"Failed to get stats: {str(e)}"}), 500 