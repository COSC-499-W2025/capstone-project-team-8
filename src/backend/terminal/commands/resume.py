"""
Resume management command handlers
Handles listing templates, generating, and viewing resumes
"""
from ..client import APIClient
from ..utils import print_success, print_error


class ResumeCommands:
    """Resume management commands"""
    
    def __init__(self, client: APIClient):
        self.client = client
    
    def list_resume_templates(self):
        """List available resume templates"""
        url = f"{self.client.api_base}/resume/templates/"
        try:
            response = self.client.session.get(url)
            if response.status_code == 200:
                templates = response.json()
                print_success("Available resume templates")
                self.client.print_json(templates)
                return templates
            else:
                print_error(f"Failed to get templates: {response.status_code}")
                return None
        except Exception as e:
            print_error(f"Error: {str(e)}")
            return None
    
    def generate_resume(self, job_description: str = ""):
        """Generate a new resume"""
        url = f"{self.client.api_base}/resume/generate/"
        data = {"job_description": job_description} if job_description else {}
        
        try:
            response = self.client.session.post(url, json=data)
            if response.status_code == 201:
                print_success("Resume generated")
                self.client.print_json(response.json())
                return response.json()
            else:
                print_error(f"Failed to generate resume: {response.status_code}")
                self.client.print_json(response.json())
                return None
        except Exception as e:
            print_error(f"Error: {str(e)}")
            return None
    
    def get_resume(self, resume_id: int):
        """Get detailed information about a resume"""
        url = f"{self.client.api_base}/resume/{resume_id}/"
        try:
            response = self.client.session.get(url)
            if response.status_code == 200:
                print_success(f"Resume {resume_id} details")
                self.client.print_json(response.json())
                return response.json()
            else:
                print_error(f"Failed to get resume: {response.status_code}")
                return None
        except Exception as e:
            print_error(f"Error: {str(e)}")
            return None
