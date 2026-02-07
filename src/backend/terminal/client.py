"""
Base API client for handling HTTP requests and authentication
"""
import requests
import json
from typing import Optional, Dict, Any


class APIClient:
    """Base API client with authentication and session management"""
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url.rstrip('/')
        self.api_base = f"{self.base_url}/api"
        self.session = requests.Session()
        self.access_token: Optional[str] = None
        self.refresh_token: Optional[str] = None
        self.username: Optional[str] = None
    
    def set_auth_headers(self):
        """Set authentication headers for requests"""
        if self.access_token:
            self.session.headers.update({
                'Authorization': f'Bearer {self.access_token}'
            })
    
    def clear_auth(self):
        """Clear authentication tokens"""
        self.access_token = None
        self.refresh_token = None
        self.username = None
        if 'Authorization' in self.session.headers:
            del self.session.headers['Authorization']
    
    def print_json(self, data: Any, indent: int = 2):
        """Pretty print JSON data"""
        print(json.dumps(data, indent=indent))
