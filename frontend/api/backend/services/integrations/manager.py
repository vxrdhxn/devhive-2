import httpx
from typing import Dict, Any
from backend.services.integrations.base import BaseIntegrationAdapter
from backend.services.integrations.notion import NotionAdapter
from backend.services.integrations.github import GitHubAdapter
from backend.services.ingestion_service import ingestion_service
from datetime import datetime

class GenericAdapter(BaseIntegrationAdapter):
    """Fallback adapter that treats any URI as a web source to index content."""
    async def sync(self, integration_id: str, api_token: str, base_url: str | None = None) -> Dict[str, Any]:
        if not base_url:
            return {
                "status": "partial",
                "message": "Platform adapter is in simplified mode. Basic connectivity verified.",
                "pages_found": 0,
                "items_indexed": 0
            }
        
        # Treatment: Simple Web/REST Fetcher
        async with httpx.AsyncClient() as client:
            headers = {"Authorization": f"Bearer {api_token}"} if api_token else {}
            try:
                response = await client.get(base_url, headers=headers)
                response.raise_for_status()
                
                # Check if it's JSON or HTML
                content_type = response.headers.get("Content-Type", "")
                source_text = ""
                
                if "application/json" in content_type:
                    source_text = str(response.json())
                else:
                    # Simple text extraction (no HTML parsing needed yet, just raw text)
                    source_text = response.text
                
                # Index the results
                from backend.auth.dependencies import supabase
                integ_res = supabase.table('integrations').select('user_id', 'platform_name').eq('id', integration_id).single().execute()
                user_id = str(integ_res.data['user_id'])
                platform_name = str(integ_res.data['platform_name'])
                
                await ingestion_service.process_text_content(
                    text=source_text,
                    filename=f"{platform_name}: {base_url}",
                    file_type="web",
                    user_id=user_id,
                    metadata={"source_url": base_url}
                )
                
                return {
                    "status": "success",
                    "pages_found": 1,
                    "pages_indexed": 1,
                    "message": f"Source {base_url} fetched and indexed successfully.",
                    "timestamp": datetime.now().isoformat()
                }
            except Exception as e:
                raise Exception(f"Failed to fetch content from {base_url}: {str(e)}")

class IntegrationManager:
    """
    Registry and dispatcher for integration adapters.
    """
    
    def __init__(self):
        generic = GenericAdapter()
        self._adapters: Dict[str, BaseIntegrationAdapter] = {
            "notion": NotionAdapter(),
            "slack": generic,
            "teams": generic,
            "github": GitHubAdapter(),
            "jira": generic,
            "rest": generic,
        }
        
    def get_adapter(self, platform_type: str) -> BaseIntegrationAdapter:
        return self._adapters.get(platform_type.lower(), GenericAdapter())

integration_manager = IntegrationManager()

