import os
import json
import base64
import hashlib
from cryptography.fernet import Fernet
from datetime import datetime, timedelta
import requests
from typing import Dict, Optional, Tuple

class TokenManager:
    def __init__(self, tokens_file: str = "secure_tokens.json"):
        self.tokens_file = tokens_file
        self.encryption_key = self._get_or_create_key()
        self.cipher = Fernet(self.encryption_key)
        self.tokens = self._load_tokens()
    
    def _get_or_create_key(self) -> bytes:
        """Get or create encryption key"""
        key_file = "encryption.key"
        if os.path.exists(key_file):
            with open(key_file, "rb") as f:
                return f.read()
        else:
            key = Fernet.generate_key()
            with open(key_file, "wb") as f:
                f.write(key)
            return key
    
    def _encrypt_token(self, token: str) -> str:
        """Encrypt a token"""
        return self.cipher.encrypt(token.encode()).decode()
    
    def _decrypt_token(self, encrypted_token: str) -> str:
        """Decrypt a token"""
        return self.cipher.decrypt(encrypted_token.encode()).decode()
    
    def _load_tokens(self) -> Dict:
        """Load tokens from file"""
        if os.path.exists(self.tokens_file):
            try:
                with open(self.tokens_file, 'r') as f:
                    encrypted_data = json.load(f)
                    decrypted_data = {}
                    for key, value in encrypted_data.items():
                        if isinstance(value, dict) and 'encrypted_token' in value:
                            decrypted_data[key] = {
                                'token': self._decrypt_token(value['encrypted_token']),
                                'stored_at': value.get('stored_at'),
                                'last_used': value.get('last_used'),
                                'is_valid': value.get('is_valid', True)
                            }
                    return decrypted_data
            except Exception as e:
                print(f"Error loading tokens: {e}")
        return {}
    
    def _save_tokens(self):
        """Save tokens to file"""
        encrypted_data = {}
        for key, value in self.tokens.items():
            encrypted_data[key] = {
                'encrypted_token': self._encrypt_token(value['token']),
                'stored_at': value.get('stored_at'),
                'last_used': value.get('last_used'),
                'is_valid': value.get('is_valid', True)
            }
        
        with open(self.tokens_file, 'w') as f:
            json.dump(encrypted_data, f, indent=2)
    
    def store_token(self, service: str, token: str) -> Tuple[bool, str]:
        """Store a token with validation"""
        try:
            # Validate token first
            is_valid, error_msg = self._validate_token(service, token)
            
            if is_valid:
                self.tokens[service] = {
                    'token': token,
                    'stored_at': datetime.now().isoformat(),
                    'last_used': datetime.now().isoformat(),
                    'is_valid': True
                }
                self._save_tokens()
                
                # Set in environment for current session
                os.environ[f"{service.upper()}_TOKEN"] = token
                
                return True, "Token stored successfully"
            else:
                return False, f"Invalid token: {error_msg}"
                
        except Exception as e:
            return False, f"Error storing token: {str(e)}"
    
    def get_token(self, service: str) -> Optional[str]:
        """Get a stored token"""
        if service in self.tokens:
            token_data = self.tokens[service]
            # Update last used time
            token_data['last_used'] = datetime.now().isoformat()
            self._save_tokens()
            
            # Set in environment for current session
            os.environ[f"{service.upper()}_TOKEN"] = token_data['token']
            
            return token_data['token']
        return None
    
    def remove_token(self, service: str) -> bool:
        """Remove a stored token"""
        if service in self.tokens:
            del self.tokens[service]
            self._save_tokens()
            
            # Remove from environment
            env_key = f"{service.upper()}_TOKEN"
            if env_key in os.environ:
                del os.environ[env_key]
            
            return True
        return False
    
    def list_tokens(self) -> Dict:
        """List all stored tokens (without showing actual tokens)"""
        token_info = {}
        for service, data in self.tokens.items():
            token_info[service] = {
                'stored_at': data.get('stored_at'),
                'last_used': data.get('last_used'),
                'is_valid': data.get('is_valid', True),
                'has_token': True
            }
        return token_info
    
    def _validate_token(self, service: str, token: str) -> Tuple[bool, str]:
        """Validate a token by making a test API call"""
        try:
            if service.lower() == "github":
                headers = {"Authorization": f"token {token}"}
                response = requests.get("https://api.github.com/user", headers=headers)
                if response.status_code == 200:
                    return True, "Valid GitHub token"
                else:
                    return False, "Invalid GitHub token"
            
            elif service.lower() == "notion":
                headers = {
                    "Authorization": f"Bearer {token}",
                    "Notion-Version": "2022-06-28",
                    "Content-Type": "application/json"
                }
                response = requests.get("https://api.notion.com/v1/users/me", headers=headers)
                if response.status_code == 200:
                    return True, "Valid Notion token"
                else:
                    error_detail = response.text if response.text else "No error details"
                    return False, f"Invalid Notion token (Status: {response.status_code}, Error: {error_detail[:100]})"
            
            elif service.lower() == "slack":
                headers = {"Authorization": f"Bearer {token}"}
                response = requests.post("https://slack.com/api/auth.test", headers=headers)
                if response.status_code == 200:
                    result = response.json()
                    if result.get('ok'):
                        return True, "Valid Slack token"
                    else:
                        return False, f"Invalid Slack token: {result.get('error', 'Unknown error')}"
                else:
                    return False, "Invalid Slack token"
            
            else:
                return False, f"Unknown service: {service}"
                
        except Exception as e:
            return False, f"Validation error: {str(e)}"
    
    def validate_stored_tokens(self) -> Dict:
        """Validate all stored tokens"""
        results = {}
        for service in list(self.tokens.keys()):
            token = self.tokens[service]['token']
            is_valid, error_msg = self._validate_token(service, token)
            
            self.tokens[service]['is_valid'] = is_valid
            results[service] = {
                'is_valid': is_valid,
                'error': error_msg if not is_valid else None
            }
        
        self._save_tokens()
        return results

# Global token manager instance
token_manager = TokenManager() 