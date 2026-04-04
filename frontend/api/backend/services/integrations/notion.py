import httpx
from typing import Dict, Any, List
from backend.services.integrations.base import BaseIntegrationAdapter
from backend.services.ingestion_service import ingestion_service
from datetime import datetime

class NotionAdapter(BaseIntegrationAdapter):
    """
    Adapter for Notion API. Fetch pages and index their content.
    """
    
    async def sync(self, integration_id: str, user_id: str, api_token: str, base_url: str = None) -> Dict[str, Any]:
        headers = {
            "Authorization": f"Bearer {api_token}",
            "Notion-Version": "2022-06-28",
            "Content-Type": "application/json"
        }
        
        async with httpx.AsyncClient() as client:
            # 1. Search for pages the integration has access to
            search_url = "https://api.notion.com/v1/search"
            try:
                response = await client.post(search_url, headers=headers, json={"filter": {"property": "object", "value": "page"}})
                response.raise_for_status()
            except Exception as e:
                raise Exception(f"Failed to connect to Notion: {str(e)}")
                
            pages = response.json().get("results", [])
            total_pages = len(pages)
            indexed_count: int = 0
            
            for page in pages:
                page_id = str(page["id"])
                # Get page title (complex in Notion JSON)
                properties = page.get("properties", {})
                title = "Untitled Page"
                for prop in properties.values():
                    if prop and isinstance(prop, dict) and prop.get("type") == "title":
                        title_array = prop.get("title", [])
                        if title_array:
                            title = "".join([t.get("plain_text", "") for t in title_array])
                
                # 2. Get Page Content (Blocks)
                blocks_url = f"https://api.notion.com/v1/blocks/{page_id}/children"
                blocks_response = await client.get(blocks_url, headers=headers)
                
                if blocks_response.status_code == 200:
                    blocks = blocks_response.json().get("results", [])
                    page_text_list: List[str] = []
                    for block in blocks:
                        # Extract text from standard block types
                        block_type = str(block.get("type", ""))
                        if block_type in ["paragraph", "heading_1", "heading_2", "heading_3", "bulleted_list_item"]:
                            inner_block = block.get(block_type, {})
                            rich_text = inner_block.get("rich_text", [])
                            text_content = "".join([t.get("plain_text", "") for t in rich_text])
                            if text_content:
                                page_text_list.append(text_content)
                    
                    page_text = "\n".join(page_text_list)
                    if page_text.strip():
                        # 3. Index via IngestionService
                        await ingestion_service.process_text_content(
                            text=page_text,
                            filename=f"Notion: {title}",
                            file_type="notion",
                            user_id=user_id,
                            metadata={"notion_page_id": page_id, "url": page.get("url")}
                        )
                        indexed_count = indexed_count + 1
            
            return {
                "status": "success",
                "pages_found": total_pages,
                "pages_indexed": indexed_count,
                "timestamp": datetime.now().isoformat()
            }
