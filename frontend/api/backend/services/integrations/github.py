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
        repo_parts = base_url.rstrip('/').split('/')
        if len(repo_parts) < 2:
            raise Exception(f"Invalid GitHub URL format: {base_url}")
        
        repo_full_name = f"{repo_parts[-2]}/{repo_parts[-1]}"
        api_base = f"https://api.github.com/repos/{repo_full_name}"
        
        headers = {
            "Accept": "application/vnd.github.v3+json",
            "User-Agent": "Dev-Hive-KTP"
        }
        if api_token:
            headers["Authorization"] = f"token {api_token}"
            
        async with httpx.AsyncClient() as client:
            # 2. Identify Default Branch
            repo_res = await client.get(api_base, headers=headers)
            repo_res.raise_for_status()
            default_branch = repo_res.json().get("default_branch", "main")
            
            # 3. Fetch Recursive Tree
            tree_url = f"{api_base}/git/trees/{default_branch}?recursive=1"
            tree_res = await client.get(tree_url, headers=headers)
            tree_res.raise_for_status()
            tree_data = tree_res.json()
            
            from backend.auth.dependencies import supabase
            integ_res = supabase.table('integrations').select('user_id').eq('id', integration_id).single().execute()
            user_id = str(integ_res.data['user_id'])
            
            indexed_count = 0
            for item in tree_data.get("tree", []):
                # Filter for documentation/text blobs
                path = item.get("path", "")
                if item.get("type") == "blob" and (path.endswith(".md") or path.endswith(".txt")):
                    # 4. Fetch Blob Content
                    blob_url = item.get("url")
                    download_res = await client.get(blob_url, headers=headers)
                    if download_res.status_code == 200:
                        f_data = download_res.json()
                        content_b64 = f_data.get("content", "")
                        encoding = f_data.get("encoding", "")
                        
                        if encoding == "base64":
                            try:
                                # GitHub base64 can contain newlines
                                text = base64.b64decode(content_b64.replace('\n', '')).decode("utf-8")
                            except Exception:
                                continue # Skip binary or malformed files
                        else:
                            text = content_b64 # Possibly already decoded or raw
                            
                        await ingestion_service.process_text_content(
                            text=text,
                            filename=f"GitHub: {repo_full_name}/{path}",
                            file_type="github",
                            user_id=user_id,
                            metadata={"github_repo": repo_full_name, "path": path, "branch": default_branch}
                        )
                        indexed_count += 1
            
            return {
                "status": "success",
                "repo": repo_full_name,
                "branch": default_branch,
                "pages_indexed": indexed_count,
                "message": f"Successfully indexed {indexed_count} files recursively from {default_branch}.",
                "timestamp": datetime.now().isoformat()
            }

