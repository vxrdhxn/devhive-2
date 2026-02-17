import os
import requests
import base64
from typing import List, Dict, Any
from dotenv import load_dotenv

load_dotenv()

class GitHubIntegration:
    def __init__(self):
        # Get token from token manager instead of environment
        from .token_manager import token_manager
        self.token = token_manager.get_token("github")
        self.api_base = "https://api.github.com"
        self.headers = {
            "Authorization": f"token {self.token}",
            "Accept": "application/vnd.github.v3+json"
        } if self.token else {}
    
    def get_repository_content(self, owner: str, repo: str, path: str = "") -> List[Dict[str, Any]]:
        """Get repository content including README, docs, and code files"""
        try:
            url = f"{self.api_base}/repos/{owner}/{repo}/contents/{path}"
            response = requests.get(url, headers=self.headers)
            
            if response.status_code == 404:
                # Path doesn't exist, return empty list
                return []
            
            response.raise_for_status()
            
            contents = []
            for item in response.json():
                if item["type"] == "file":
                    # Only process text files
                    if self._is_text_file(item["name"]):
                        file_content = self.get_file_content(owner, repo, item["path"])
                        if file_content:
                            contents.append({
                                "name": item["name"],
                                "path": item["path"],
                                "content": file_content,
                                "type": "file",
                                "size": item["size"]
                            })
                elif item["type"] == "dir":
                    # Recursively get directory contents
                    sub_contents = self.get_repository_content(owner, repo, item["path"])
                    contents.extend(sub_contents)
            
            return contents
        except Exception as e:
            # Only print error if it's not a 404 (which is expected for missing paths)
            if "404" not in str(e):
                print(f"Error getting repository content for {owner}/{repo}/{path}: {e}")
            return []
    
    def get_file_content(self, owner: str, repo: str, path: str) -> str:
        """Get content of a specific file"""
        try:
            url = f"{self.api_base}/repos/{owner}/{repo}/contents/{path}"
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()
            
            content_data = response.json()
            if content_data["encoding"] == "base64":
                # Decode base64 content
                binary_content = base64.b64decode(content_data["content"])
                
                # Check if it's a text file by trying to decode as UTF-8
                try:
                    content = binary_content.decode("utf-8")
                    return content
                except UnicodeDecodeError:
                    # File is binary, skip it
                    return ""
            return ""
        except Exception as e:
            print(f"Error getting file content for {path}: {e}")
            return ""
    
    def get_issues(self, owner: str, repo: str, state: str = "all") -> List[Dict[str, Any]]:
        """Get repository issues and pull requests"""
        try:
            url = f"{self.api_base}/repos/{owner}/{repo}/issues"
            params = {"state": state, "per_page": 100}
            response = requests.get(url, headers=self.headers, params=params)
            response.raise_for_status()
            
            issues = []
            for issue in response.json():
                issues.append({
                    "title": issue["title"],
                    "body": issue["body"] or "",
                    "number": issue["number"],
                    "state": issue["state"],
                    "type": "pull_request" if "pull_request" in issue else "issue",
                    "created_at": issue["created_at"],
                    "updated_at": issue["updated_at"]
                })
            
            return issues
        except Exception as e:
            print(f"Error getting issues: {e}")
            return []
    
    def get_readme(self, owner: str, repo: str) -> str:
        """Get repository README"""
        try:
            url = f"{self.api_base}/repos/{owner}/{repo}/readme"
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()
            
            content_data = response.json()
            if content_data["encoding"] == "base64":
                content = base64.b64decode(content_data["content"]).decode("utf-8")
                return content
            return ""
        except Exception as e:
            print(f"Error getting README: {e}")
            return ""
    
    def _is_text_file(self, filename: str) -> bool:
        """Check if a file is text-based and should be processed"""
        text_extensions = {
            '.md', '.txt', '.rst', '.adoc', '.asciidoc',  # Documentation
            '.py', '.js', '.ts', '.jsx', '.tsx', '.vue',  # Code
            '.java', '.c', '.cpp', '.h', '.hpp', '.cs',   # More code
            '.php', '.rb', '.go', '.rs', '.swift',        # More code
            '.json', '.yaml', '.yml', '.xml', '.html',    # Data/Config
            '.css', '.scss', '.sass', '.less',            # Styles
            '.sql', '.sh', '.bat', '.ps1', '.yml',        # Scripts/Config
            '.dockerfile', '.gitignore', '.gitattributes' # Config
        }
        
        # Check file extension
        if any(filename.lower().endswith(ext) for ext in text_extensions):
            return True
        
        # Check for common text file names without extensions
        text_filenames = {
            'readme', 'license', 'changelog', 'contributing',
            'code_of_conduct', 'security', 'dockerfile', 'makefile'
        }
        
        if filename.lower() in text_filenames:
            return True
        
        return False

    def search_repositories(self, query: str, language: str = None) -> List[Dict[str, Any]]:
        """Search for repositories"""
        try:
            url = f"{self.api_base}/search/repositories"
            params = {"q": query, "per_page": 10}
            if language:
                params["q"] += f" language:{language}"
            
            response = requests.get(url, headers=self.headers, params=params)
            response.raise_for_status()
            
            repos = []
            for repo in response.json()["items"]:
                repos.append({
                    "name": repo["name"],
                    "full_name": repo["full_name"],
                    "description": repo["description"],
                    "language": repo["language"],
                    "stars": repo["stargazers_count"],
                    "forks": repo["forks_count"]
                })
            
            return repos
        except Exception as e:
            print(f"Error searching repositories: {e}")
            return []

def extract_text_from_markdown(content: str) -> str:
    """Extract plain text from markdown content"""
    import re
    
    # Remove markdown syntax
    content = re.sub(r'#+\s*', '', content)  # Headers
    content = re.sub(r'\*\*(.*?)\*\*', r'\1', content)  # Bold
    content = re.sub(r'\*(.*?)\*', r'\1', content)  # Italic
    content = re.sub(r'`(.*?)`', r'\1', content)  # Inline code
    content = re.sub(r'```.*?```', '', content, flags=re.DOTALL)  # Code blocks
    content = re.sub(r'\[([^\]]+)\]\([^)]+\)', r'\1', content)  # Links
    content = re.sub(r'!\[([^\]]*)\]\([^)]+\)', '', content)  # Images
    
    return content.strip()

def get_github_data(owner: str, repo: str) -> List[Dict[str, Any]]:
    """Get comprehensive GitHub data for a repository - ALL documents"""
    github = GitHubIntegration()
    
    # Note: GitHub token is optional for public repos
    if not github.token:
        print("⚠️  No GitHub token found. Using public API (rate limited).")
    
    data = []
    
    print(f"📚 Reading ALL documents from {owner}/{repo}...")
    
    # Get README
    try:
        readme_content = github.get_readme(owner, repo)
        if readme_content:
            data.append({
                "title": f"{owner}/{repo} - README",
                "content": extract_text_from_markdown(readme_content),
                "source": f"github://{owner}/{repo}/README.md",
                "type": "documentation"
            })
            print(f"✅ Added README")
    except Exception as e:
        print(f"⚠️  Could not get README for {owner}/{repo}: {e}")
    
    # Get ALL files from the entire repository (recursive)
    try:
        print("🔍 Scanning entire repository for documents...")
        all_files = github.get_repository_content(owner, repo, "")
        
        file_count = 0
        for file in all_files:
            if file["type"] == "file":
                # Process all text files, not just specific ones
                if github._is_text_file(file["name"]):
                    file_count += 1
                    data.append({
                        "title": f"{owner}/{repo} - {file['name']}",
                        "content": extract_text_from_markdown(file["content"]),
                        "source": f"github://{owner}/{repo}/{file['path']}",
                        "type": "code" if file["name"].endswith(('.py', '.js', '.ts', '.java', '.cpp', '.c', '.h', '.cs', '.php', '.rb', '.go', '.rs', '.swift')) else "documentation"
                    })
        
        print(f"✅ Added {file_count} files from repository")
        
    except Exception as e:
        print(f"⚠️  Could not get all repository files for {owner}/{repo}: {e}")
    
    # Get issues and discussions (more comprehensive)
    try:
        print("📋 Reading issues and discussions...")
        issues = github.get_issues(owner, repo)
        issue_count = 0
        for issue in issues[:50]:  # Increased limit to 50
            if issue["body"] and len(issue["body"]) > 50:  # Only meaningful issues
                issue_count += 1
                data.append({
                    "title": f"{owner}/{repo} - Issue #{issue['number']}: {issue['title']}",
                    "content": issue["body"],
                    "source": f"github://{owner}/{repo}/issues/{issue['number']}",
                    "type": "issue"
                })
        print(f"✅ Added {issue_count} issues")
    except Exception as e:
        print(f"⚠️  Could not get issues for {owner}/{repo}: {e}")
    
    print(f"📊 Total documents found: {len(data)}")
    return data
