"""
Project management command handlers
Handles listing, viewing, and managing projects
"""
from ..client import APIClient
from ..utils import print_success, print_error


class ProjectCommands:
    """Project management commands"""
    
    def __init__(self, client: APIClient):
        self.client = client
    
    def list_projects(self):
        """List all user projects"""
        url = f"{self.client.api_base}/projects/"
        try:
            response = self.client.session.get(url)
            if response.status_code == 200:
                projects = response.json()
                print_success(f"Found {len(projects)} projects")
                self.client.print_json(projects)
                return projects
            else:
                print_error(f"Failed to list projects: {response.status_code}")
                return None
        except Exception as e:
            print_error(f"Error: {str(e)}")
            return None
    
    def get_project(self, project_id: int):
        """Get detailed information about a specific project"""
        url = f"{self.client.api_base}/projects/{project_id}/"
        try:
            response = self.client.session.get(url)
            if response.status_code == 200:
                print_success(f"Project {project_id} details")
                self.client.print_json(response.json())
                return response.json()
            else:
                print_error(f"Failed to get project: {response.status_code}")
                return None
        except Exception as e:
            print_error(f"Error: {str(e)}")
            return None
    
    def get_project_stats(self):
        """Get statistics about user's projects"""
        url = f"{self.client.api_base}/projects/stats/"
        try:
            response = self.client.session.get(url)
            if response.status_code == 200:
                print_success("Project statistics")
                self.client.print_json(response.json())
                return response.json()
            else:
                print_error(f"Failed to get stats: {response.status_code}")
                return None
        except Exception as e:
            print_error(f"Error: {str(e)}")
            return None
    
    def get_ranked_projects(self):
        """Get projects ranked by importance"""
        url = f"{self.client.api_base}/projects/ranked/"
        try:
            response = self.client.session.get(url)
            if response.status_code == 200:
                projects = response.json()
                print_success("Ranked projects")
                self.client.print_json(projects)
                return projects
            else:
                print_error(f"Failed to get ranked projects: {response.status_code}")
                return None
        except Exception as e:
            print_error(f"Error: {str(e)}")
            return None
    
    def get_top_projects_summary(self):
        """Get summary of top projects"""
        url = f"{self.client.api_base}/projects/ranked/summary/"
        try:
            response = self.client.session.get(url)
            if response.status_code == 200:
                print_success("Top projects summary")
                self.client.print_json(response.json())
                return response.json()
            else:
                print_error(f"Failed to get summary: {response.status_code}")
                return None
        except Exception as e:
            print_error(f"Error: {str(e)}")
            return None
    
    def delete_project(self, project_id: int):
        """Delete a project"""
        url = f"{self.client.api_base}/projects/{project_id}/"
        try:
            response = self.client.session.delete(url)
            if response.status_code == 204:
                print_success(f"Project {project_id} deleted")
                return True
            else:
                print_error(f"Failed to delete project: {response.status_code}")
                return False
        except Exception as e:
            print_error(f"Error: {str(e)}")
            return False
