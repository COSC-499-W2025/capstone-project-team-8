"""
User management command handlers
Handles user profile, password changes, and user queries
"""
from ..client import APIClient
from ..utils import print_success, print_error


class UserCommands:
    """User management commands"""
    
    def __init__(self, client: APIClient):
        self.client = client
    
    def get_current_user(self):
        """Get current user information"""
        url = f"{self.client.api_base}/users/me/"
        try:
            response = self.client.session.get(url)
            if response.status_code == 200:
                print_success("User information retrieved")
                self.client.print_json(response.json())
                return response.json()
            else:
                print_error(f"Failed to get user info: {response.status_code}")
                self.client.print_json(response.json())
                return None
        except Exception as e:
            print_error(f"Error: {str(e)}")
            return None
    
    def get_public_user(self, username: str):
        """Get public user profile"""
        url = f"{self.client.api_base}/users/{username}/"
        try:
            response = self.client.session.get(url)
            if response.status_code == 200:
                print_success(f"Profile for {username}")
                self.client.print_json(response.json())
                return response.json()
            else:
                print_error(f"User not found: {response.status_code}")
                return None
        except Exception as e:
            print_error(f"Error: {str(e)}")
            return None
    
    def change_password(self, old_password: str, new_password: str):
        """Change user password"""
        url = f"{self.client.api_base}/users/password/"
        data = {"old_password": old_password, "new_password": new_password}
        
        try:
            response = self.client.session.post(url, json=data)
            if response.status_code == 200:
                print_success("Password changed successfully")
                return True
            else:
                print_error(f"Password change failed: {response.status_code}")
                self.client.print_json(response.json())
                return False
        except Exception as e:
            print_error(f"Error: {str(e)}")
            return False
