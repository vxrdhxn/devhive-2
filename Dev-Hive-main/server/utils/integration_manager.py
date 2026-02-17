import os
import uuid
import datetime
from typing import List, Dict, Any, Optional
from dotenv import load_dotenv

from .github_utils import get_github_data
from .notion_utils import get_notion_data
from .slack_utils import get_slack_data
from .enhanced_chunker import (
    chunk_text, 
    deduplicate_chunks, 
    merge_chunks_from_sources,
    create_pinecone_vectors,
    generate_content_hash
)
from .openai_utils import get_embedding
from .pinecone_utils import upsert_chunks, query_chunks

load_dotenv()

class IntegrationManager:
    """Manages integration of multiple data sources with deduplication"""
    
    def __init__(self):
        self.source_priority = {
            "github": 1,  # Highest priority
            "notion": 2,  # Medium priority
            "slack": 3    # Lowest priority
        }
    
    def integrate_github(self, owner: str, repo: str) -> Dict[str, Any]:
        """Integrate GitHub repository data"""
        try:
            print(f"📦 Integrating GitHub: {owner}/{repo}")
            
            # Get GitHub data
            github_data = get_github_data(owner, repo)
            
            if not github_data:
                return {
                    "success": False,
                    "error": "No data found or GitHub token not configured",
                    "chunks_processed": 0,
                    "chunks_stored": 0
                }
            
            # Process and store data
            total_chunks = 0
            stored_chunks = 0
            
            for item in github_data:
                chunks = chunk_text(item["content"], max_tokens=300, overlap=50)
                
                vectors = []
                for chunk in chunks:
                    embedding = get_embedding(chunk["text"])
                    vector_data = {
                        "id": chunk["id"],
                        "values": embedding,
                        "metadata": {
                            "text": chunk["text"],
                            "content_hash": chunk["content_hash"],
                            "title": item["title"],
                            "source": item["source"],
                            "type": item["type"],
                            "integration": "github",
                            "source_name": "github",
                            "chunk_index": chunk["chunk_index"],
                            "sentence_count": chunk["sentence_count"],
                            "word_count": chunk["word_count"],
                            "start_pos": chunk["start_pos"],
                            "end_pos": chunk["end_pos"],
                            "integration_timestamp": datetime.datetime.now().isoformat(),
                            "timestamp": datetime.datetime.now().isoformat()
                        }
                    }
                    vectors.append(vector_data)
                
                # Check for duplicates before upserting
                unique_vectors = self._deduplicate_vectors(vectors)
                
                # Only upsert if there are vectors to upsert
                if unique_vectors:
                    upsert_chunks(unique_vectors)
                
                total_chunks += len(chunks)
                stored_chunks += len(unique_vectors)
            
            return {
                "success": True,
                "source": f"github://{owner}/{repo}",
                "documents_processed": len(github_data),
                "chunks_processed": total_chunks,
                "chunks_stored": stored_chunks,
                "duplicates_removed": total_chunks - stored_chunks,
                "integration": "github"
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"GitHub integration failed: {str(e)}",
                "chunks_processed": 0,
                "chunks_stored": 0
            }
    
    def integrate_notion(self, search_query: str = "", page_ids: List[str] = None, 
                        database_ids: List[str] = None, read_all_workspace: bool = False) -> Dict[str, Any]:
        """Integrate Notion data"""
        try:
            print(f"📝 Integrating Notion data...")
            
            # Get Notion data
            notion_data = get_notion_data(
                search_query=search_query,
                page_ids=page_ids if page_ids else None,
                database_ids=database_ids if database_ids else None,
                read_all_workspace=read_all_workspace
            )
            
            if not notion_data:
                return {
                    "success": False,
                    "error": "No data found or Notion token not configured",
                    "chunks_processed": 0,
                    "chunks_stored": 0
                }
            
            # Process and store data
            total_chunks = 0
            stored_chunks = 0
            
            for item in notion_data:
                chunks = chunk_text(item["content"], max_tokens=300, overlap=50)
                
                vectors = []
                for chunk in chunks:
                    embedding = get_embedding(chunk["text"])
                    vector_data = {
                        "id": chunk["id"],
                        "values": embedding,
                        "metadata": {
                            "text": chunk["text"],
                            "content_hash": chunk["content_hash"],
                            "title": item["title"],
                            "source": item["source"],
                            "type": item["type"],
                            "integration": "notion",
                            "source_name": "notion",
                            "chunk_index": chunk["chunk_index"],
                            "sentence_count": chunk["sentence_count"],
                            "word_count": chunk["word_count"],
                            "start_pos": chunk["start_pos"],
                            "end_pos": chunk["end_pos"],
                            "integration_timestamp": datetime.datetime.now().isoformat(),
                            "timestamp": datetime.datetime.now().isoformat()
                        }
                    }
                    vectors.append(vector_data)
                
                # Check for duplicates before upserting
                unique_vectors = self._deduplicate_vectors(vectors)
                
                # Only upsert if there are vectors to upsert
                if unique_vectors:
                    upsert_chunks(unique_vectors)
                
                total_chunks += len(chunks)
                stored_chunks += len(unique_vectors)
            
            return {
                "success": True,
                "source": "notion://workspace",
                "documents_processed": len(notion_data),
                "chunks_processed": total_chunks,
                "chunks_stored": stored_chunks,
                "duplicates_removed": total_chunks - stored_chunks,
                "integration": "notion"
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"Notion integration failed: {str(e)}",
                "chunks_processed": 0,
                "chunks_stored": 0
            }
    
    def integrate_slack(self, channel_ids: List[str] = None, search_query: str = None, 
                       include_dms: bool = False) -> Dict[str, Any]:
        """Integrate Slack data"""
        try:
            print(f"💬 Integrating Slack data...")
            
            # Get Slack data
            slack_data = get_slack_data(
                channel_ids=channel_ids if channel_ids else None,
                search_query=search_query if search_query else None,
                include_dms=include_dms
            )
            
            if not slack_data:
                return {
                    "success": False,
                    "error": "No data found or Slack token not configured",
                    "chunks_processed": 0,
                    "chunks_stored": 0
                }
            
            # Process and store data
            total_chunks = 0
            stored_chunks = 0
            
            for item in slack_data:
                chunks = chunk_text(item["content"], max_tokens=300, overlap=50)
                
                vectors = []
                for chunk in chunks:
                    embedding = get_embedding(chunk["text"])
                    vector_data = {
                        "id": chunk["id"],
                        "values": embedding,
                        "metadata": {
                            "text": chunk["text"],
                            "content_hash": chunk["content_hash"],
                            "title": item["title"],
                            "source": item["source"],
                            "type": item["type"],
                            "integration": "slack",
                            "source_name": "slack",
                            "chunk_index": chunk["chunk_index"],
                            "sentence_count": chunk["sentence_count"],
                            "word_count": chunk["word_count"],
                            "start_pos": chunk["start_pos"],
                            "end_pos": chunk["end_pos"],
                            "integration_timestamp": datetime.datetime.now().isoformat(),
                            "timestamp": item.get("timestamp", datetime.datetime.now().isoformat())
                        }
                    }
                    vectors.append(vector_data)
                
                # Check for duplicates before upserting
                unique_vectors = self._deduplicate_vectors(vectors)
                
                # Only upsert if there are vectors to upsert
                if unique_vectors:
                    upsert_chunks(unique_vectors)
                
                total_chunks += len(chunks)
                stored_chunks += len(unique_vectors)
            
            return {
                "success": True,
                "source": "slack://workspace",
                "messages_processed": len(slack_data),
                "chunks_processed": total_chunks,
                "chunks_stored": stored_chunks,
                "duplicates_removed": total_chunks - stored_chunks,
                "integration": "slack"
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"Slack integration failed: {str(e)}",
                "chunks_processed": 0,
                "chunks_stored": 0
            }
    
    def integrate_all_sources(self, github_config: Dict[str, Any] = None, 
                            notion_config: Dict[str, Any] = None,
                            slack_config: Dict[str, Any] = None) -> Dict[str, Any]:
        """Integrate all sources with comprehensive deduplication"""
        try:
            print("🚀 Starting comprehensive integration of all sources...")
            
            results = {
                "success": True,
                "integrations": [],
                "total_chunks_processed": 0,
                "total_chunks_stored": 0,
                "total_duplicates_removed": 0,
                "sources_integrated": []
            }
            
            # Integrate GitHub
            if github_config:
                github_result = self.integrate_github(
                    github_config.get("owner"),
                    github_config.get("repo")
                )
                results["integrations"].append(github_result)
                if github_result["success"]:
                    results["sources_integrated"].append("github")
                    results["total_chunks_processed"] += github_result.get("chunks_processed", 0)
                    results["total_chunks_stored"] += github_result.get("chunks_stored", 0)
                    results["total_duplicates_removed"] += github_result.get("duplicates_removed", 0)
            
            # Integrate Notion
            if notion_config:
                notion_result = self.integrate_notion(
                    search_query=notion_config.get("search_query", ""),
                    page_ids=notion_config.get("page_ids", []),
                    database_ids=notion_config.get("database_ids", []),
                    read_all_workspace=notion_config.get("read_all_workspace", False)
                )
                results["integrations"].append(notion_result)
                if notion_result["success"]:
                    results["sources_integrated"].append("notion")
                    results["total_chunks_processed"] += notion_result.get("chunks_processed", 0)
                    results["total_chunks_stored"] += notion_result.get("chunks_stored", 0)
                    results["total_duplicates_removed"] += notion_result.get("duplicates_removed", 0)
            
            # Integrate Slack
            if slack_config:
                slack_result = self.integrate_slack(
                    channel_ids=slack_config.get("channel_ids", []),
                    search_query=slack_config.get("search_query", ""),
                    include_dms=slack_config.get("include_dms", False)
                )
                results["integrations"].append(slack_result)
                if slack_result["success"]:
                    results["sources_integrated"].append("slack")
                    results["total_chunks_processed"] += slack_result.get("chunks_processed", 0)
                    results["total_chunks_stored"] += slack_result.get("chunks_stored", 0)
                    results["total_duplicates_removed"] += slack_result.get("duplicates_removed", 0)
            
            print(f"✅ Integration completed!")
            print(f"   📊 Total chunks processed: {results['total_chunks_processed']}")
            print(f"   📊 Total chunks stored: {results['total_chunks_stored']}")
            print(f"   🗑️  Duplicates removed: {results['total_duplicates_removed']}")
            print(f"   🔗 Sources integrated: {', '.join(results['sources_integrated'])}")
            
            return results
            
        except Exception as e:
            return {
                "success": False,
                "error": f"Comprehensive integration failed: {str(e)}",
                "integrations": [],
                "total_chunks_processed": 0,
                "total_chunks_stored": 0,
                "total_duplicates_removed": 0,
                "sources_integrated": []
            }
    
    def _deduplicate_vectors(self, vectors: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Remove duplicate vectors based on content hash"""
        seen_hashes = set()
        unique_vectors = []
        
        for vector in vectors:
            content_hash = vector["metadata"].get("content_hash")
            if content_hash and content_hash not in seen_hashes:
                seen_hashes.add(content_hash)
                unique_vectors.append(vector)
        
        return unique_vectors
    
    def get_integration_stats(self) -> Dict[str, Any]:
        """Get statistics about integrated data"""
        try:
            # Query Pinecone to get stats
            # This is a simplified version - you might want to implement more detailed stats
            stats = {
                "total_vectors": 0,
                "sources": {
                    "github": 0,
                    "notion": 0,
                    "slack": 0
                },
                "types": {},
                "recent_integrations": []
            }
            
            # You could implement more detailed stats here
            # For now, return basic structure
            
            return stats
            
        except Exception as e:
            return {
                "error": f"Failed to get stats: {str(e)}"
            }

# Global instance
integration_manager = IntegrationManager() 