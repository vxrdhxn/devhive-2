from fastapi import APIRouter, Depends, HTTPException
from typing import List, Dict, Any
from backend.auth.dependencies import require_admin_or_manager, supabase
import anyio
from datetime import datetime, timedelta

try:
    from gotrue import User
except ImportError:
    from gotrue.types import User

router = APIRouter(prefix="/analytics", tags=["analytics"])

@router.get("/stats")
async def get_overview_stats(current_user: User = Depends(require_admin_or_manager)):
    """Get high-level summary metrics for the dashboard."""
    if not supabase:
        raise HTTPException(status_code=500, detail="Supabase not configured")

    # 1. Total Queries
    queries_res = await anyio.to_thread.run_sync(
        lambda: supabase.table("query_logs").select("id", count="exact").execute()
    )
    total_queries = queries_res.count if queries_res.count is not None else 0

    # 2. Average Confidence (only for queries that have it)
    try:
        conf_res = await anyio.to_thread.run_sync(
            lambda: supabase.table("query_logs").select("confidence").not_.is_("confidence", "null").execute()
        )
        conf_data = conf_res.data or []
        avg_confidence = sum(c['confidence'] for c in conf_data) / len(conf_data) if conf_data else 0
    except Exception as e:
        print(f"Warning: Failed to fetch confidence (is the column missing?): {e}")
        avg_confidence = 0

    # 3. Active Users (unique user_ids in logs)
    users_res = await anyio.to_thread.run_sync(
        lambda: supabase.table("query_logs").select("user_id").execute()
    )
    active_users_count = len(set(u['user_id'] for u in users_res.data)) if users_res.data else 0

    return {
        "total_queries": total_queries,
        "avg_confidence": round(avg_confidence, 2),
        "active_users": active_users_count,
        "timestamp": datetime.now().isoformat()
    }

@router.get("/trends")
async def get_query_trends(current_user: User = Depends(require_admin_or_manager)):
    """Get query counts over the last 7-30 days with a guaranteed timeline."""
    if not supabase:
        raise HTTPException(status_code=500, detail="Supabase not configured")

    # 1. Fetch last 30 days of logs
    thirty_days_ago = (datetime.now() - timedelta(days=30)).replace(hour=0, minute=0, second=0).isoformat()
    
    logs_res = await anyio.to_thread.run_sync(
        lambda: supabase.table("query_logs").select("created_at").gte("created_at", thirty_days_ago).execute()
    )
    
    # 2. Count logs per date
    raw_trends = {}
    for log in (logs_res.data or []):
        date_str = log['created_at'].split('T')[0]
        raw_trends[date_str] = raw_trends.get(date_str, 0) + 1
        
    # 3. Create a GUARANTEED timeline for at least the last 7 days
    chart_data = []
    today = datetime.now().date()
    for i in range(29, -1, -1): # Last 30 days
        d = today - timedelta(days=i)
        date_str = d.isoformat()
        
        # Only include dates that have data, OR the most recent 7 days to keep it clean
        if date_str in raw_trends or i < 7:
            chart_data.append({
                "date": d.strftime("%b %d"), # Formatting for better axis display
                "queries": raw_trends.get(date_str, 0)
            })
    
    return chart_data

@router.get("/top-terms")
async def get_top_terms(current_user: User = Depends(require_admin_or_manager)):
    """Get most frequent search terms."""
    if not supabase:
        raise HTTPException(status_code=500, detail="Supabase not configured")

    logs_res = await anyio.to_thread.run_sync(
        lambda: supabase.table("query_logs").select("query").execute()
    )
    
    counts = {}
    for log in (logs_res.data or []):
        query = log['query'].strip().lower()
        if len(query) > 3: # Ignore very short queries
            counts[query] = counts.get(query, 0) + 1
            
    # Sort and take top 10
    top_entries = sorted(counts.items(), key=lambda x: x[1], reverse=True)[:10]
    return [{"term": k, "count": v} for k, v in top_entries]
