from abc import ABC, abstractmethod
from typing import List, Dict, Any

class BaseIntegrationAdapter(ABC):
    """
    Abstract base class for all integration adapters (Notion, Jira, etc.)
    """
    
    @abstractmethod
    async def sync(self, integration_id: str, api_token: str, base_url: str = None) -> Dict[str, Any]:
        """
        Synchronize data from the external platform and index it.
        Returns a summary of the sync process.
        """
        pass
