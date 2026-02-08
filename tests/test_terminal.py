import os
import sys
import unittest
from unittest.mock import Mock, patch, MagicMock
import json

# Add the backend directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src', 'backend'))

from terminal.client import APIClient
from terminal.commands.auth import AuthCommands
from terminal.commands.user import UserCommands
from terminal.commands.project import ProjectCommands
from terminal.commands.portfolio import PortfolioCommands
from terminal.commands.resume import ResumeCommands
from terminal.commands.upload import UploadCommands
from terminal.utils import Colors, print_success, print_error, print_info, print_warning


class TestAPIClient(unittest.TestCase):
    """Test suite for APIClient base class"""
    
    def setUp(self):
        """Set up test client"""
        self.client = APIClient("http://localhost:8000")
    
    def test_client_initialization(self):
        """Test that client initializes with correct base URLs"""
        self.assertEqual(self.client.base_url, "http://localhost:8000")
        self.assertEqual(self.client.api_base, "http://localhost:8000/api")
        self.assertIsNone(self.client.access_token)
        self.assertIsNone(self.client.refresh_token)
        self.assertIsNone(self.client.username)
    
    def test_set_auth_headers(self):
        """Test that auth headers are set correctly"""
        self.client.access_token = "test_token_123"
        self.client.set_auth_headers()
        
        self.assertIn('Authorization', self.client.session.headers)
        self.assertEqual(
            self.client.session.headers['Authorization'],
            'Bearer test_token_123'
        )
    
    def test_clear_auth(self):
        """Test that auth is cleared properly"""
        self.client.access_token = "test_token"
        self.client.refresh_token = "refresh_token"
        self.client.username = "testuser"
        self.client.set_auth_headers()
        
        self.client.clear_auth()
        
        self.assertIsNone(self.client.access_token)
        self.assertIsNone(self.client.refresh_token)
        self.assertIsNone(self.client.username)
        self.assertNotIn('Authorization', self.client.session.headers)
    
    def test_print_json(self):
        """Test JSON printing helper"""
        test_data = {"key": "value", "number": 123}
        # Should not raise an exception
        self.client.print_json(test_data)


class TestAuthCommands(unittest.TestCase):
    """Test suite for AuthCommands"""
    
    def setUp(self):
        """Set up test client and auth commands"""
        self.client = APIClient("http://localhost:8000")
        self.auth = AuthCommands(self.client)
    
    @patch('terminal.commands.auth.print_success')
    @patch('requests.Session.post')
    def test_signup_success(self, mock_post, mock_print):
        """Test successful user signup"""
        mock_response = Mock()
        mock_response.status_code = 201
        mock_response.json.return_value = {
            "username": "newuser",
            "email": "new@example.com"
        }
        mock_post.return_value = mock_response
        
        result = self.auth.signup(
            "newuser",
            "new@example.com",
            "password123",
            "password123"
        )
        
        self.assertIsNotNone(result)
        self.assertEqual(result["username"], "newuser")
        mock_print.assert_called_once()
    
    @patch('terminal.commands.auth.print_success')
    @patch('terminal.commands.auth.print_info')
    @patch('requests.Session.post')
    def test_login_success(self, mock_post, mock_info, mock_success):
        """Test successful login"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "access": "access_token_xyz",
            "refresh": "refresh_token_abc"
        }
        mock_post.return_value = mock_response
        
        result = self.auth.login("testuser", "password123")
        
        self.assertIsNotNone(result)
        self.assertEqual(self.client.access_token, "access_token_xyz")
        self.assertEqual(self.client.refresh_token, "refresh_token_abc")
        self.assertEqual(self.client.username, "testuser")
    
    @patch('terminal.commands.auth.print_error')
    @patch('requests.Session.post')
    def test_login_failure(self, mock_post, mock_error):
        """Test failed login"""
        mock_response = Mock()
        mock_response.status_code = 401
        mock_response.json.return_value = {"detail": "Invalid credentials"}
        mock_post.return_value = mock_response
        
        result = self.auth.login("baduser", "wrongpass")
        
        self.assertIsNone(result)
        self.assertIsNone(self.client.access_token)
        mock_error.assert_called()
    
    @patch('terminal.commands.auth.print_success')
    @patch('requests.Session.post')
    def test_refresh_token(self, mock_post, mock_success):
        """Test token refresh"""
        self.client.refresh_token = "old_refresh_token"
        
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"access": "new_access_token"}
        mock_post.return_value = mock_response
        
        result = self.auth.refresh_access_token()
        
        self.assertTrue(result)
        self.assertEqual(self.client.access_token, "new_access_token")


class TestUserCommands(unittest.TestCase):
    """Test suite for UserCommands"""
    
    def setUp(self):
        """Set up test client and user commands"""
        self.client = APIClient("http://localhost:8000")
        self.user = UserCommands(self.client)
    
    @patch('terminal.commands.user.print_success')
    @patch('requests.Session.get')
    def test_get_current_user(self, mock_get, mock_success):
        """Test getting current user info"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "username": "currentuser",
            "email": "current@example.com"
        }
        mock_get.return_value = mock_response
        
        result = self.user.get_current_user()
        
        self.assertIsNotNone(result)
        self.assertEqual(result["username"], "currentuser")
    
    @patch('terminal.commands.user.print_success')
    @patch('requests.Session.post')
    def test_change_password_success(self, mock_post, mock_success):
        """Test successful password change"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_post.return_value = mock_response
        
        result = self.user.change_password("oldpass", "newpass")
        
        self.assertTrue(result)


class TestProjectCommands(unittest.TestCase):
    """Test suite for ProjectCommands"""
    
    def setUp(self):
        """Set up test client and project commands"""
        self.client = APIClient("http://localhost:8000")
        self.project = ProjectCommands(self.client)
    
    @patch('terminal.commands.project.print_success')
    @patch('requests.Session.get')
    def test_list_projects(self, mock_get, mock_success):
        """Test listing projects"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = [
            {"id": 1, "name": "Project 1"},
            {"id": 2, "name": "Project 2"}
        ]
        mock_get.return_value = mock_response
        
        result = self.project.list_projects()
        
        self.assertIsNotNone(result)
        self.assertEqual(len(result), 2)
    
    @patch('terminal.commands.project.print_success')
    @patch('requests.Session.get')
    def test_get_project(self, mock_get, mock_success):
        """Test getting specific project"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "id": 1,
            "name": "Test Project",
            "description": "A test"
        }
        mock_get.return_value = mock_response
        
        result = self.project.get_project(1)
        
        self.assertIsNotNone(result)
        self.assertEqual(result["id"], 1)
    
    @patch('terminal.commands.project.print_success')
    @patch('requests.Session.delete')
    def test_delete_project(self, mock_delete, mock_success):
        """Test deleting a project"""
        mock_response = Mock()
        mock_response.status_code = 204
        mock_delete.return_value = mock_response
        
        result = self.project.delete_project(1)
        
        self.assertTrue(result)


class TestPortfolioCommands(unittest.TestCase):
    """Test suite for PortfolioCommands"""
    
    def setUp(self):
        """Set up test client and portfolio commands"""
        self.client = APIClient("http://localhost:8000")
        self.portfolio = PortfolioCommands(self.client)
    
    @patch('terminal.commands.portfolio.print_success')
    @patch('requests.Session.get')
    def test_list_portfolios(self, mock_get, mock_success):
        """Test listing portfolios"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = [
            {"id": 1, "name": "Portfolio 1"}
        ]
        mock_get.return_value = mock_response
        
        result = self.portfolio.list_portfolios()
        
        self.assertIsNotNone(result)
        self.assertEqual(len(result), 1)
    
    @patch('terminal.commands.portfolio.print_success')
    @patch('requests.Session.post')
    def test_generate_portfolio(self, mock_post, mock_success):
        """Test generating a portfolio"""
        mock_response = Mock()
        mock_response.status_code = 201
        mock_response.json.return_value = {
            "id": 1,
            "name": "New Portfolio"
        }
        mock_post.return_value = mock_response
        
        result = self.portfolio.generate_portfolio("New Portfolio", "Description")
        
        self.assertIsNotNone(result)
        self.assertEqual(result["name"], "New Portfolio")


class TestResumeCommands(unittest.TestCase):
    """Test suite for ResumeCommands"""
    
    def setUp(self):
        """Set up test client and resume commands"""
        self.client = APIClient("http://localhost:8000")
        self.resume = ResumeCommands(self.client)
    
    @patch('terminal.commands.resume.print_success')
    @patch('requests.Session.get')
    def test_list_templates(self, mock_get, mock_success):
        """Test listing resume templates"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = [
            {"id": 1, "name": "Template 1"}
        ]
        mock_get.return_value = mock_response
        
        result = self.resume.list_resume_templates()
        
        self.assertIsNotNone(result)
    
    @patch('terminal.commands.resume.print_success')
    @patch('requests.Session.post')
    def test_generate_resume(self, mock_post, mock_success):
        """Test generating a resume"""
        mock_response = Mock()
        mock_response.status_code = 201
        mock_response.json.return_value = {
            "id": 1,
            "content": "Resume content"
        }
        mock_post.return_value = mock_response
        
        result = self.resume.generate_resume("Job description")
        
        self.assertIsNotNone(result)


class TestUploadCommands(unittest.TestCase):
    """Test suite for UploadCommands"""
    
    def setUp(self):
        """Set up test client and upload commands"""
        self.client = APIClient("http://localhost:8000")
        self.upload = UploadCommands(self.client)
    
    @patch('terminal.commands.upload.print_error')
    def test_upload_zip_file_not_found(self, mock_error):
        """Test uploading non-existent zip file"""
        result = self.upload.upload_zip("/nonexistent/file.zip")
        
        self.assertIsNone(result)
        mock_error.assert_called()
    
    @patch('terminal.commands.upload.print_error')
    def test_upload_zip_wrong_extension(self, mock_error):
        """Test uploading file without .zip extension"""
        result = self.upload.upload_zip("test.txt")
        
        self.assertIsNone(result)
        mock_error.assert_called()
    
    @patch('terminal.commands.upload.print_success')
    @patch('requests.Session.get')
    def test_get_api_schema(self, mock_get, mock_success):
        """Test getting API schema"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "openapi": "3.0.0",
            "info": {"title": "API"},
            "paths": {"/endpoint1/": {}, "/endpoint2/": {}}
        }
        mock_get.return_value = mock_response
        
        result = self.upload.get_api_schema()
        
        self.assertIsNotNone(result)
        self.assertEqual(result["openapi"], "3.0.0")


class TestUtilities(unittest.TestCase):
    """Test suite for utility functions"""
    
    def test_colors_defined(self):
        """Test that color codes are defined"""
        self.assertIsNotNone(Colors.GREEN)
        self.assertIsNotNone(Colors.RED)
        self.assertIsNotNone(Colors.YELLOW)
        self.assertIsNotNone(Colors.CYAN)
        self.assertIsNotNone(Colors.BOLD)
    
    def test_print_functions_dont_crash(self):
        """Test that print functions execute without error"""
        # These should not raise exceptions
        print_success("Success message")
        print_error("Error message")
        print_info("Info message")
        print_warning("Warning message")


if __name__ == '__main__':
    unittest.main()
