import httpx
import base64
from typing import Dict, Any, List
from backend.services.integrations.base import BaseIntegrationAdapter
from backend.services.ingestion_service import ingestion_service
from datetime import datetime

class GitHubAdapter(BaseIntegrationAdapter):
    """
    Adapter for GitHub API. Fetches documents (README, markdown, code) and indexes them.
    """
    
    async def sync(self, integration_id: str, api_token: str, base_url: str = None) -> Dict[str, Any]:
        if not base_url:
            raise Exception("GitHub requires a repository URL in the Endpoint URI field")
            
        # 1. Parse repository Owner and Name from URL
        # e.g. https://github.com/google/guava -> google/guava
        repo_parts = base_url.rstrip('/').split('/')
        if len(repo_parts) < 2:
            raise Exception(f"Invalid GitHub URL format: {base_url}")
        
        # Pull the last two parts for Owner/Repo
        repo_full_name = f"{repo_parts[-2]}/{repo_parts[-1]}"
        api_base = f"https://api.github.com/repos/{repo_full_name}"
        
        headers = {
            "Accept": "application/vnd.github.v3+json",
            "User-Agent": "Dev-Hive-KTP"
        }
        
        # Add basic auth if token is provided
        if api_token:
            headers["Authorization"] = f"token {api_token}"
            
        async with httpx.AsyncClient() as client:
            # 2. Fetch Root Contents
            contents_url = f"{api_base}/contents"
            try:
                res = await client.get(contents_url, headers=headers)
                res.raise_for_status()
                files = res.json()
                
                from backend.auth.dependencies import supabase
                integ_res = supabase.table('integrations').select('user_id').eq('id', integration_id).single().execute()
                user_id = str(integ_res.data['user_id'])
                
                indexed_count = 0
                for file_info in files:
                    # Filter for documentation/text files
                    name = str(file_info.get("name", ""))
                    if file_info.get("type") == "file" and (name.endswith(".md") or name.endswith(".txt")):
                        # Fetch individual file content
                        download_res = await client.get(file_info["url"], headers=headers)
                        if download_res.status_code == 200:
                            f_data = download_res.json()
                            content_b64 = f_data.get("content", "")
                            text = base64.b64decode(content_b64).decode("utf-8")
                            
                            await ingestion_service.process_text_content(
                                text=text,
                                filename=f"GitHub: {repo_full_name}/{name}",
                                file_type="github",
                                user_id=user_id,
                                metadata={"github_repo": repo_full_name, "path": name}
                            )
                            indexed_count += 1
                
                return {
                    "status": "success",
                    "repo": repo_full_name,
                    "pages_indexed": indexed_count,
                    "message": f"Successfully indexed {indexed_count} files from the repository root.",
                    "timestamp": datetime.now().isoformat()
                }
                
            except Exception as e:
                # Fallback to README if listing fails or returns error
                raise Exception(f"Failed to extract repository content: {str(e)}")

