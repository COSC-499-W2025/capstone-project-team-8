"""
Authentication command handlers
Handles login, signup, logout, and token refresh
"""
from ..client import APIClient
from ..utils import print_success, print_error, print_info, print_warning


class AuthCommands:
    """Authentication-related commands"""
    
    def __init__(self, client: APIClient):
        self.client = client
    
    def signup(self, username: str, email: str, password: str, 
               confirm_password: str, first_name: str = "", last_name: str = ""):
        """Register a new user account"""
        url = f"{self.client.api_base}/signup/"
        data = {
            "username": username,
            "email": email,
            "password": password,
            "confirm_password": confirm_password,
            "first_name": first_name,
            "last_name": last_name
        }
        
        try:
            response = self.client.session.post(url, json=data)
            if response.status_code == 201:
                print_success(f"Account created successfully for {username}")
                self.client.print_json(response.json())
                return response.json()
            else:
                print_error(f"Signup failed: {response.status_code}")
                self.client.print_json(response.json())
                return None
        except Exception as e:
            print_error(f"Signup error: {str(e)}")
            return None
    
    def login(self, username: str, password: str):
        """Login and obtain JWT tokens"""
        url = f"{self.client.api_base}/token/"
        data = {"username": username, "password": password}
        
        try:
            response = self.client.session.post(url, json=data)
            if response.status_code == 200:
                result = response.json()
                self.client.access_token = result.get('access')
                self.client.refresh_token = result.get('refresh')
                self.client.username = username
                self.client.set_auth_headers()
                print_success(f"Logged in as {username}")
                print_info(f"Access token: {self.client.access_token[:20]}...")
                return result
            else:
                print_error(f"Login failed: {response.status_code}")
                self.client.print_json(response.json())
                return None
        except Exception as e:
            print_error(f"Login error: {str(e)}")
            return None
    
    def logout(self):
        """Logout and invalidate tokens"""
        if not self.client.refresh_token:
            print_warning("Not logged in")
            return
        
        url = f"{self.client.api_base}/token/logout/"
        data = {"refresh": self.client.refresh_token}
        
        try:
            response = self.client.session.post(url, json=data)
            print_success("Logged out successfully")
            self.client.clear_auth()
        except Exception as e:
            print_error(f"Logout error: {str(e)}")
            self.client.clear_auth()
    
    def refresh_access_token(self):
        """Refresh the access token using refresh token"""
        if not self.client.refresh_token:
            print_error("No refresh token available")
            return False
        
        url = f"{self.client.api_base}/token/refresh/"
        data = {"refresh": self.client.refresh_token}
        
        try:
            response = self.client.session.post(url, json=data)
            if response.status_code == 200:
                result = response.json()
                self.client.access_token = result.get('access')
                self.client.set_auth_headers()
                print_success("Access token refreshed")
                return True
            else:
                print_error("Token refresh failed")
                return False
        except Exception as e:
            print_error(f"Token refresh error: {str(e)}")
            return False
