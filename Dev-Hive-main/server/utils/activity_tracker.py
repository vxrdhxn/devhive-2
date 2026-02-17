import json
import os
from datetime import datetime
from typing import List, Dict, Any

class ActivityTracker:
    """Track project activities for timeline display"""
    
    def __init__(self, activity_file: str = "activity_log.json"):
        self.activity_file = activity_file
        self._ensure_activity_file()
    
    def _ensure_activity_file(self):
        """Ensure activity log file exists"""
        if not os.path.exists(self.activity_file):
            with open(self.activity_file, 'w') as f:
                json.dump([], f)
    
    def log_activity(self, activity_type: str, description: str, details: Dict[str, Any] = None):
        """Log a new activity"""
        activity = {
            "timestamp": datetime.now().isoformat(),
            "type": activity_type,
            "description": description,
            "details": details or {}
        }
        
        # Read existing activities
        try:
            with open(self.activity_file, 'r') as f:
                activities = json.load(f)
        except (json.JSONDecodeError, FileNotFoundError):
            activities = []
        
        # Add new activity
        activities.append(activity)
        
        # Keep only last 100 activities
        if len(activities) > 100:
            activities = activities[-100:]
        
        # Write back to file
        with open(self.activity_file, 'w') as f:
            json.dump(activities, f, indent=2)
    
    def get_activities(self, limit: int = 20) -> List[Dict[str, Any]]:
        """Get recent activities"""
        try:
            with open(self.activity_file, 'r') as f:
                activities = json.load(f)
        except (json.JSONDecodeError, FileNotFoundError):
            return []
        
        # Sort by timestamp (newest first)
        activities.sort(key=lambda x: x.get('timestamp', ''), reverse=True)
        
        return activities[:limit]
    
    def get_activities_by_type(self, activity_type: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Get activities filtered by type"""
        activities = self.get_activities(limit * 2)  # Get more to filter
        filtered = [a for a in activities if a.get('type') == activity_type]
        return filtered[:limit]

# Global activity tracker instance
activity_tracker = ActivityTracker()

# Activity type constants
ACTIVITY_TYPES = {
    "integration": "🔗 Integration",
    "upload": "📤 Upload",
    "search": "🔍 Search",
    "qa": "❓ Q&A",
    "system": "⚙️ System"
}

def log_integration_activity(source: str, chunks_stored: int, duplicates_removed: int = 0):
    """Log integration activity"""
    description = f"Integrated {source} data"
    details = {
        "source": source,
        "chunks_stored": chunks_stored,
        "duplicates_removed": duplicates_removed
    }
    activity_tracker.log_activity("integration", description, details)

def log_upload_activity(content_type: str, title: str, chunks_stored: int):
    """Log upload activity"""
    description = f"Uploaded {content_type}: {title}"
    details = {
        "content_type": content_type,
        "title": title,
        "chunks_stored": chunks_stored
    }
    activity_tracker.log_activity("upload", description, details)

def log_search_activity(query: str, results_count: int):
    """Log search activity"""
    description = f"Searched for: {query[:50]}{'...' if len(query) > 50 else ''}"
    details = {
        "query": query,
        "results_count": results_count
    }
    activity_tracker.log_activity("search", description, details)

def log_qa_activity(question: str, sources_used: int):
    """Log Q&A activity"""
    description = f"Asked: {question[:50]}{'...' if len(question) > 50 else ''}"
    details = {
        "question": question,
        "sources_used": sources_used
    }
    activity_tracker.log_activity("qa", description, details)

def log_system_activity(description: str, details: Dict[str, Any] = None):
    """Log system activity"""
    activity_tracker.log_activity("system", description, details or {}) 