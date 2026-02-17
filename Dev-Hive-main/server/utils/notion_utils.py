import os
import requests
from typing import List, Dict, Any
from dotenv import load_dotenv

load_dotenv()

class NotionIntegration:
    def __init__(self):
        # Get token from token manager instead of environment
        from .token_manager import token_manager
        self.token = token_manager.get_token("notion")
        self.api_base = "https://api.notion.com/v1"
        self.headers = {
            "Authorization": f"Bearer {self.token}",
            "Notion-Version": "2022-06-28",
            "Content-Type": "application/json"
        } if self.token else {}
    
    def get_all_workspace_pages(self, max_pages: int = 100) -> List[Dict[str, Any]]:
        """Get all pages in the workspace"""
        try:
            url = f"{self.api_base}/search"
            data = {
                "filter": {
                    "value": "page",
                    "property": "object"
                },
                "page_size": 100,
                "sort": {
                    "direction": "descending",
                    "timestamp": "last_edited_time"
                }
            }
            
            all_pages = []
            has_more = True
            start_cursor = None
            
            while has_more and len(all_pages) < max_pages:
                if start_cursor:
                    data["start_cursor"] = start_cursor
                
                response = requests.post(url, headers=self.headers, json=data)
                response.raise_for_status()
                
                result = response.json()
                pages = result["results"]
                
                for page in pages:
                    all_pages.append({
                        "id": page["id"],
                        "title": self._extract_title(page),
                        "url": page["url"],
                        "created_time": page["created_time"],
                        "last_edited_time": page["last_edited_time"]
                    })
                
                has_more = result.get("has_more", False)
                start_cursor = result.get("next_cursor")
            
            print(f"📚 Found {len(all_pages)} pages in workspace")
            return all_pages
            
        except Exception as e:
            print(f"Error getting all workspace pages: {e}")
            return []
    
    def search_pages(self, query: str = "", filter_type: str = "page") -> List[Dict[str, Any]]:
        """Search for pages in Notion"""
        try:
            url = f"{self.api_base}/search"
            data = {
                "query": query,
                "filter": {
                    "value": filter_type,
                    "property": "object"
                },
                "page_size": 100
            }
            
            response = requests.post(url, headers=self.headers, json=data)
            response.raise_for_status()
            
            pages = []
            for page in response.json()["results"]:
                pages.append({
                    "id": page["id"],
                    "title": self._extract_title(page),
                    "url": page["url"],
                    "created_time": page["created_time"],
                    "last_edited_time": page["last_edited_time"]
                })
            
            return pages
        except Exception as e:
            print(f"Error searching Notion pages: {e}")
            return []
    
    def get_page_content(self, page_id: str) -> Dict[str, Any]:
        """Get content of a specific page"""
        try:
            # Get page properties
            page_url = f"{self.api_base}/pages/{page_id}"
            page_response = requests.get(page_url, headers=self.headers)
            page_response.raise_for_status()
            page_data = page_response.json()
            
            # Get page blocks
            blocks_url = f"{self.api_base}/blocks/{page_id}/children"
            blocks_response = requests.get(blocks_url, headers=self.headers)
            blocks_response.raise_for_status()
            blocks_data = blocks_response.json()
            
            # Extract text content
            content = self._extract_text_from_blocks(blocks_data["results"])
            
            return {
                "id": page_id,
                "title": self._extract_title(page_data),
                "content": content,
                "url": page_data["url"],
                "created_time": page_data["created_time"],
                "last_edited_time": page_data["last_edited_time"]
            }
        except Exception as e:
            print(f"Error getting page content: {e}")
            return {}
    
    def get_database_pages(self, database_id: str) -> List[Dict[str, Any]]:
        """Get all pages from a database"""
        try:
            url = f"{self.api_base}/databases/{database_id}/query"
            data = {"page_size": 100}
            
            response = requests.post(url, headers=self.headers, json=data)
            response.raise_for_status()
            
            pages = []
            for page in response.json()["results"]:
                page_content = self.get_page_content(page["id"])
                if page_content:
                    pages.append(page_content)
            
            return pages
        except Exception as e:
            print(f"Error getting database pages: {e}")
            return []
    
    def _extract_title(self, page_data: Dict[str, Any]) -> str:
        """Extract title from page properties"""
        try:
            properties = page_data.get("properties", {})
            
            # Look for title property
            for prop_name, prop_data in properties.items():
                if prop_data["type"] == "title" and prop_data["title"]:
                    return " ".join([text["plain_text"] for text in prop_data["title"]])
                
                # Also check for name property (common in databases)
                if prop_name.lower() in ["name", "title"] and prop_data.get("title"):
                    return " ".join([text["plain_text"] for text in prop_data["title"]])
            
            return "Untitled"
        except:
            return "Untitled"
    
    def _extract_text_from_blocks(self, blocks: List[Dict[str, Any]]) -> str:
        """Extract text content from page blocks"""
        text_parts = []
        
        for block in blocks:
            block_type = block["type"]
            
            if block_type == "paragraph":
                text = self._extract_rich_text(block["paragraph"]["rich_text"])
                if text:
                    text_parts.append(text)
            
            elif block_type == "heading_1":
                text = self._extract_rich_text(block["heading_1"]["rich_text"])
                if text:
                    text_parts.append(f"# {text}")
            
            elif block_type == "heading_2":
                text = self._extract_rich_text(block["heading_2"]["rich_text"])
                if text:
                    text_parts.append(f"## {text}")
            
            elif block_type == "heading_3":
                text = self._extract_rich_text(block["heading_3"]["rich_text"])
                if text:
                    text_parts.append(f"### {text}")
            
            elif block_type == "bulleted_list_item":
                text = self._extract_rich_text(block["bulleted_list_item"]["rich_text"])
                if text:
                    text_parts.append(f"• {text}")
            
            elif block_type == "numbered_list_item":
                text = self._extract_rich_text(block["numbered_list_item"]["rich_text"])
                if text:
                    text_parts.append(f"1. {text}")
            
            elif block_type == "quote":
                text = self._extract_rich_text(block["quote"]["rich_text"])
                if text:
                    text_parts.append(f"> {text}")
            
            elif block_type == "code":
                text = self._extract_rich_text(block["code"]["rich_text"])
                if text:
                    text_parts.append(f"```\n{text}\n```")
            
            elif block_type == "callout":
                text = self._extract_rich_text(block["callout"]["rich_text"])
                if text:
                    text_parts.append(f"💡 {text}")
            
            # Recursively process child blocks
            if "children" in block and block["has_children"]:
                child_blocks = self._get_child_blocks(block["id"])
                child_text = self._extract_text_from_blocks(child_blocks)
                if child_text:
                    text_parts.append(child_text)
        
        return "\n\n".join(text_parts)
    
    def _extract_rich_text(self, rich_text: List[Dict[str, Any]]) -> str:
        """Extract plain text from rich text array"""
        return "".join([text["plain_text"] for text in rich_text])
    
    def _get_child_blocks(self, block_id: str) -> List[Dict[str, Any]]:
        """Get child blocks of a block"""
        try:
            url = f"{self.api_base}/blocks/{block_id}/children"
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()
            return response.json()["results"]
        except:
            return []

def get_notion_data(search_query: str = "", page_ids: List[str] = None, database_ids: List[str] = None, read_all_workspace: bool = False) -> List[Dict[str, Any]]:
    """Get comprehensive Notion data"""
    notion = NotionIntegration()
    
    if not notion.token:
        raise Exception("Notion token not found. Set NOTION_TOKEN in .env")
    
    data = []
    
    # Read all workspace pages if requested
    if read_all_workspace:
        print("🔍 Reading all pages in Notion workspace...")
        workspace_pages = notion.get_all_workspace_pages()
        
        for page in workspace_pages:
            print(f"📄 Processing page: {page['title']}")
            content = notion.get_page_content(page["id"])
            if content and content["content"]:
                data.append({
                    "title": content["title"],
                    "content": content["content"],
                    "source": f"notion://{content['url']}",
                    "type": "page"
                })
                print(f"✅ Added page: {content['title']}")
            else:
                print(f"⚠️  Skipped empty page: {page['title']}")
    
    # Search for pages
    elif search_query:
        pages = notion.search_pages(search_query)
        for page in pages[:10]:  # Limit to 10 pages
            content = notion.get_page_content(page["id"])
            if content and content["content"]:
                data.append({
                    "title": content["title"],
                    "content": content["content"],
                    "source": f"notion://{content['url']}",
                    "type": "page"
                })
    
    # Get specific pages
    elif page_ids:
        for page_id in page_ids:
            content = notion.get_page_content(page_id)
            if content and content["content"]:
                data.append({
                    "title": content["title"],
                    "content": content["content"],
                    "source": f"notion://{content['url']}",
                    "type": "page"
                })
    
    # Get database pages
    elif database_ids:
        for db_id in database_ids:
            pages = notion.get_database_pages(db_id)
            for page in pages:
                if page["content"]:
                    data.append({
                        "title": page["title"],
                        "content": page["content"],
                        "source": f"notion://{page['url']}",
                        "type": "database_entry"
                    })
    
    print(f"📊 Total Notion pages processed: {len(data)}")
    return data 