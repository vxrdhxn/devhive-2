import os
import requests
from typing import List, Dict, Any
from dotenv import load_dotenv

load_dotenv()

class SlackIntegration:
    def __init__(self):
        # Get token from token manager instead of environment
        from .token_manager import token_manager
        self.token = token_manager.get_token("slack")
        self.api_base = "https://slack.com/api"
        
        if not self.token:
            raise Exception("Slack bot token not found. Set SLACK_BOT_TOKEN in .env")
    
    def get_channels(self) -> List[Dict[str, Any]]:
        """Get all channels the bot has access to"""
        try:
            url = f"{self.api_base}/conversations.list"
            params = {
                "token": self.token,
                "types": "public_channel",
                "limit": 100
            }
            
            response = requests.post(url, data=params)
            response.raise_for_status()
            
            data = response.json()
            if not data.get("ok"):
                error = data.get('error', 'Unknown error')
                print(f"❌ Slack API error getting channels: {error}")
                if error == "missing_scope":
                    print("   🔧 Missing scope: channels:read")
                elif error == "not_authed":
                    print("   🔧 Check your bot token")
                return []
            
            channels = []
            for channel in data.get("channels", []):
                channels.append({
                    "id": channel["id"],
                    "name": channel["name"],
                    "is_private": channel.get("is_private", False),
                    "num_members": channel.get("num_members", 0)
                })
            
            return channels
        except Exception as e:
            print(f"❌ Error getting Slack channels: {e}")
            return []
    
    def get_channel_messages(self, channel_id: str, limit: int = 100) -> List[Dict[str, Any]]:
        """Get messages from a specific channel"""
        try:
            url = f"{self.api_base}/conversations.history"
            params = {
                "token": self.token,
                "channel": channel_id,
                "limit": limit
            }
            
            response = requests.post(url, data=params)
            response.raise_for_status()
            
            data = response.json()
            if not data.get("ok"):
                error = data.get('error', 'Unknown error')
                print(f"❌ Slack API error getting messages for channel {channel_id}: {error}")
                if error == "missing_scope":
                    print("   🔧 Missing scope: channels:history")
                elif error == "channel_not_found":
                    print("   🔧 Channel not found")
                elif error == "not_in_channel":
                    print("   🔧 Bot not in channel - trying to read public channel history")
                    # For public channels, we should still be able to read history
                    # Let's try with a different approach
                    return self._get_public_channel_history(channel_id, limit)
                elif error == "not_authed":
                    print("   🔧 Check your bot token")
                return []
            
            messages = []
            for message in data.get("messages", []):
                # Skip bot messages and system messages
                if message.get("bot_id") or message.get("subtype"):
                    continue
                
                content = self._extract_message_content(message)
                if content and len(content.strip()) > 5:  # Reduced minimum length to match test_all_channels.py
                    messages.append({
                        "id": message["ts"],
                        "content": content,
                        "user": message.get("user", "Unknown"),
                        "timestamp": message["ts"],
                        "channel_id": channel_id
                    })
            
            return messages
        except Exception as e:
            print(f"❌ Error getting channel messages: {e}")
            return []
    
    def _get_public_channel_history(self, channel_id: str, limit: int = 100) -> List[Dict[str, Any]]:
        """Get message history from public channels even if bot is not a member"""
        try:
            # Try to get channel info first
            url = f"{self.api_base}/conversations.info"
            params = {
                "token": self.token,
                "channel": channel_id
            }
            
            response = requests.post(url, data=params)
            response.raise_for_status()
            
            data = response.json()
            if not data.get("ok"):
                print(f"❌ Cannot get info for channel {channel_id}")
                return []
            
            channel_info = data.get("channel", {})
            if channel_info.get("is_private", True):
                print(f"   ⚠️  Channel {channel_id} is private - bot needs to be invited")
                return []
            
            # For public channels, try to get history using search API as fallback
            print(f"   📢 Channel {channel_id} is public - attempting to read history")
            
            # Try conversations.history again with different parameters
            url = f"{self.api_base}/conversations.history"
            params = {
                "token": self.token,
                "channel": channel_id,
                "limit": limit,
                "inclusive": True
            }
            
            response = requests.post(url, data=params)
            response.raise_for_status()
            
            data = response.json()
            if data.get("ok"):
                messages = []
                for message in data.get("messages", []):
                    # Skip bot messages and system messages
                    if message.get("bot_id") or message.get("subtype"):
                        continue
                    
                    content = self._extract_message_content(message)
                    if content and len(content.strip()) > 5:  # Reduced minimum length to match test_all_channels.py
                        messages.append({
                            "id": message["ts"],
                            "content": content,
                            "user": message.get("user", "Unknown"),
                            "timestamp": message["ts"],
                            "channel_id": channel_id
                        })
                
                return messages
            else:
                print(f"   ❌ Still cannot read history for channel {channel_id}")
                return []
                
        except Exception as e:
            print(f"❌ Error getting public channel history: {e}")
            return []
    
    def get_direct_messages(self, limit: int = 50) -> List[Dict[str, Any]]:
        """Get recent direct messages"""
        try:
            url = f"{self.api_base}/im.list"
            params = {
                "token": self.token,
                "limit": 100
            }
            
            response = requests.post(url, data=params)
            response.raise_for_status()
            
            data = response.json()
            if not data.get("ok"):
                raise Exception(f"Slack API error: {data.get('error')}")
            
            all_messages = []
            for dm in data.get("ims", [])[:5]:  # Limit to 5 DMs
                dm_messages = self.get_channel_messages(dm["id"], limit=20)
                all_messages.extend(dm_messages)
            
            return all_messages
        except Exception as e:
            print(f"Error getting direct messages: {e}")
            return []
    
    def search_messages(self, query: str, limit: int = 50) -> List[Dict[str, Any]]:
        """Search messages across all accessible channels using conversations.history"""
        try:
            # Since search:read is not available, we'll get messages from available channels
            # and filter them locally for the search query
            channels = self.get_channels()
            all_messages = []
            
            for channel in channels[:5]:  # Limit to 5 channels for performance
                messages = self.get_channel_messages(channel["id"], limit=20)
                for message in messages:
                    # Simple text search in message content
                    if query.lower() in message["content"].lower():
                        all_messages.append({
                            "id": message["id"],
                            "content": message["content"],
                            "user": message["user"],
                            "timestamp": message["timestamp"],
                            "channel": channel["name"],
                            "permalink": f"slack://channel/{channel['id']}/messages/{message['id']}"
                        })
                
                if len(all_messages) >= limit:
                    break
            
            return all_messages[:limit]
        except Exception as e:
            print(f"Error searching messages: {e}")
            return []
    
    def get_files(self, channel_id: str = None, limit: int = 20) -> List[Dict[str, Any]]:
        """Get files shared in channels or workspace"""
        try:
            url = f"{self.api_base}/files.list"
            params = {
                "token": self.token,
                "limit": limit
            }
            
            if channel_id:
                params["channel"] = channel_id
            
            response = requests.post(url, data=params)
            response.raise_for_status()
            
            data = response.json()
            if not data.get("ok"):
                raise Exception(f"Slack API error: {data.get('error')}")
            
            files = []
            for file in data.get("files", []):
                if file.get("filetype") in ["text", "markdown", "pdf", "doc"]:
                    files.append({
                        "id": file["id"],
                        "name": file["name"],
                        "title": file.get("title", file["name"]),
                        "filetype": file.get("filetype"),
                        "size": file.get("size", 0),
                        "url_private": file.get("url_private"),
                        "permalink": file.get("permalink")
                    })
            
            return files
        except Exception as e:
            print(f"Error getting files: {e}")
            return []
    
    def _extract_message_content(self, message: Dict[str, Any]) -> str:
        """Extract clean text content from a Slack message"""
        try:
            content = message.get("text", "")
            
            # Remove user mentions
            import re
            content = re.sub(r'<@[A-Z0-9]+>', '', content)
            
            # Remove channel mentions
            content = re.sub(r'<#[A-Z0-9]+\|[^>]+>', '', content)
            
            # Remove URLs
            content = re.sub(r'<https?://[^>]+>', '', content)
            
            # Remove formatting
            content = re.sub(r'\*([^*]+)\*', r'\1', content)  # Bold
            content = re.sub(r'_([^_]+)_', r'\1', content)    # Italic
            content = re.sub(r'`([^`]+)`', r'\1', content)    # Code
            
            # Clean up whitespace
            content = re.sub(r'\s+', ' ', content).strip()
            
            return content
        except:
            return ""

def get_slack_data(channel_ids: List[str] = None, search_query: str = None, include_dms: bool = False) -> List[Dict[str, Any]]:
    """Get comprehensive Slack data with detailed debugging"""
    try:
        slack = SlackIntegration()
        print(f"✅ Slack integration initialized successfully")
    except Exception as e:
        print(f"❌ Slack integration error: {e}")
        return []
    
    data = []
    
    # Get messages from specific channels
    if channel_ids:
        print(f"📢 Processing {len(channel_ids)} specific channels...")
        for channel_id in channel_ids:
            messages = slack.get_channel_messages(channel_id, limit=100)  # Increased limit
            print(f"   📢 Channel {channel_id}: {len(messages)} messages")
            
            # Show sample messages for debugging
            if messages:
                print(f"      💬 Sample messages from channel {channel_id}:")
                for i, msg in enumerate(messages[:3]):
                    print(f"         {i+1}. [{msg['user']}] {msg['content'][:80]}...")
                if len(messages) > 3:
                    print(f"         ... and {len(messages) - 3} more messages")
            
            for message in messages:
                data.append({
                    "title": f"Slack - Channel Message - {message['user']}",
                    "content": message["content"],
                    "source": f"slack://channel/{channel_id}/messages/{message['id']}",
                    "type": "channel_message",
                    "timestamp": message["timestamp"]
                })
    
    # Search messages
    if search_query:
        print(f"🔍 Searching for: '{search_query}'...")
        search_results = slack.search_messages(search_query, limit=50)  # Increased limit
        print(f"   🔍 Found {len(search_results)} search results")
        
        # Show sample search results for debugging
        if search_results:
            print(f"      💬 Sample search results:")
            for i, msg in enumerate(search_results[:3]):
                print(f"         {i+1}. [{msg['user']}] {msg['content'][:80]}...")
            if len(search_results) > 3:
                print(f"         ... and {len(search_results) - 3} more results")
        
        for message in search_results:
            data.append({
                "title": f"Slack - Search Result - {message['user']}",
                "content": message["content"],
                "source": f"slack://search/{message['id']}",
                "type": "search_result",
                "timestamp": message["timestamp"]
            })
    
    # Get direct messages
    if include_dms:
        print(f"💬 Getting direct messages...")
        dm_messages = slack.get_direct_messages(limit=50)  # Increased limit
        print(f"   💬 Found {len(dm_messages)} direct messages")
        
        # Show sample DM messages for debugging
        if dm_messages:
            print(f"      💬 Sample direct messages:")
            for i, msg in enumerate(dm_messages[:3]):
                print(f"         {i+1}. [{msg['user']}] {msg['content'][:80]}...")
            if len(dm_messages) > 3:
                print(f"         ... and {len(dm_messages) - 3} more messages")
        
        for message in dm_messages:
            data.append({
                "title": f"Slack - Direct Message - {message['user']}",
                "content": message["content"],
                "source": f"slack://dm/{message['channel_id']}/messages/{message['id']}",
                "type": "direct_message",
                "timestamp": message["timestamp"]
            })
    
    # If no specific channels, get from ALL available channels
    if not channel_ids and not search_query and not include_dms:
        print(f"📢 No specific channels provided, getting from ALL available channels...")
        channels = slack.get_channels()
        print(f"   📢 Found {len(channels)} available channels")
        
        if not channels:
            print("   ⚠️  No channels found. Make sure the bot has access to channels.")
            return []
        
        # Show all channels for debugging
        print(f"   📋 Available channels:")
        for i, channel in enumerate(channels):
            print(f"      {i+1:2d}. #{channel['name']} (ID: {channel['id']}) - {'Private' if channel.get('is_private') else 'Public'} - {channel.get('num_members', 0)} members")
        
        total_messages = 0
        all_messages = []
        
        # Process ALL channels, not just first 5
        for i, channel in enumerate(channels):
            print(f"   📢 Processing channel {i+1}/{len(channels)}: #{channel['name']} (ID: {channel['id']})")
            messages = slack.get_channel_messages(channel["id"], limit=100)  # Increased limit
            print(f"      💬 Found {len(messages)} messages in #{channel['name']}")
            
            # Show sample messages for debugging
            if messages:
                print(f"      💬 Sample messages from #{channel['name']}:")
                for j, msg in enumerate(messages[:2]):  # Show first 2 messages
                    print(f"         {j+1}. [{msg['user']}] {msg['content'][:80]}...")
                if len(messages) > 2:
                    print(f"         ... and {len(messages) - 2} more messages")
            
            total_messages += len(messages)
            all_messages.extend(messages)
            
            for message in messages:
                data.append({
                    "title": f"Slack - {channel['name']} - {message['user']}",
                    "content": message["content"],
                    "source": f"slack://channel/{channel['id']}/messages/{message['id']}",
                    "type": "channel_message",
                    "timestamp": message["timestamp"]
                })
        
        print(f"   📊 Total messages collected from {len(channels)} channels: {total_messages}")
        
        # Show comprehensive summary
        print(f"   📊 Comprehensive Summary:")
        print(f"      - Channels processed: {len(channels)}")
        print(f"      - Total messages: {total_messages}")
        print(f"      - Average messages per channel: {total_messages / len(channels) if channels else 0:.1f}")
        
        # Show all messages in detail for debugging
        print(f"   💬 ALL MESSAGES DETAILED VIEW:")
        for i, msg in enumerate(all_messages):
            print(f"      {i+1:3d}. Channel: #{msg['channel_id']} | User: {msg['user']} | Content: {msg['content'][:100]}...")
    
    print(f"📊 Total Slack data items collected: {len(data)}")
    return data 