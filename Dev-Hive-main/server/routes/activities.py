from flask import Blueprint, jsonify
from utils.activity_tracker import activity_tracker

activities_bp = Blueprint('activities', __name__)

@activities_bp.route("/activities", methods=["GET"])
def get_activities():
    """Get recent activities for timeline"""
    try:
        limit = 20  # Default limit
        activities = activity_tracker.get_activities(limit)
        
        # Format activities for frontend
        formatted_activities = []
        for activity in activities:
            formatted_activity = {
                "timestamp": activity.get("timestamp"),
                "type": activity.get("type"),
                "description": activity.get("description"),
                "details": activity.get("details", {}),
                "time_ago": _get_time_ago(activity.get("timestamp"))
            }
            formatted_activities.append(formatted_activity)
        
        return jsonify({
            "status": "success",
            "activities": formatted_activities,
            "total": len(formatted_activities)
        })
        
    except Exception as e:
        return jsonify({
            "error": f"Failed to retrieve activities: {str(e)}"
        }), 500

def _get_time_ago(timestamp_str):
    """Calculate time ago from timestamp"""
    from datetime import datetime, timezone
    import time
    
    try:
        # Parse timestamp
        dt = datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
        now = datetime.now(timezone.utc)
        
        # Calculate difference
        diff = now - dt
        
        # Convert to seconds
        seconds = diff.total_seconds()
        
        if seconds < 60:
            return "just now"
        elif seconds < 3600:
            minutes = int(seconds // 60)
            return f"{minutes}m ago"
        elif seconds < 86400:
            hours = int(seconds // 3600)
            return f"{hours}h ago"
        else:
            days = int(seconds // 86400)
            return f"{days}d ago"
            
    except Exception:
        return "recently" 