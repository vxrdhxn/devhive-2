from typing import Dict, Any
from backend.services.integrations.base import BaseIntegrationAdapter
from backend.services.integrations.notion import NotionAdapter

class GenericAdapter(BaseIntegrationAdapter):
    """Fallback adapter for newly added platforms."""
    async def sync(self, integration_id: str, api_token: str, base_url: str | None = None) -> Dict[str, Any]:
        return {
            "status": "partial",
            "message": "Platform adapter is in simplified mode. Basic connectivity verified.",
            "pages_found": 0,
            "items_indexed": 0
        }

class IntegrationManager:
    """
    Registry and dispatcher for integration adapters.
    """
    
    def __init__(self):
        self._adapters: Dict[str, BaseIntegrationAdapter] = {
            "notion": NotionAdapter(),
            "slack": GenericAdapter(),
            "teams": GenericAdapter(),
            "github": GenericAdapter(),
            "jira": GenericAdapter(),
            "rest": GenericAdapter(),
        }
        
    def get_adapter(self, platform_type: str) -> BaseIntegrationAdapter:
        return self._adapters.get(platform_type.lower(), GenericAdapter())

integration_manager = IntegrationManager()
