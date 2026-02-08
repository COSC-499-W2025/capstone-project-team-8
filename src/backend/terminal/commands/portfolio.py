"""
Portfolio management command handlers
Handles listing, generating, and managing portfolios
"""
from ..client import APIClient
from ..utils import print_success, print_error


class PortfolioCommands:
    """Portfolio management commands"""
    
    def __init__(self, client: APIClient):
        self.client = client
    
    def list_portfolios(self):
        """List all user portfolios"""
        url = f"{self.client.api_base}/portfolio/"
        try:
            response = self.client.session.get(url)
            if response.status_code == 200:
                portfolios = response.json()
                print_success(f"Found {len(portfolios)} portfolios")
                self.client.print_json(portfolios)
                return portfolios
            else:
                print_error(f"Failed to list portfolios: {response.status_code}")
                return None
        except Exception as e:
            print_error(f"Error: {str(e)}")
            return None
    
    def generate_portfolio(self, name: str, description: str = ""):
        """Generate a new portfolio"""
        url = f"{self.client.api_base}/portfolio/generate/"
        data = {"name": name, "description": description}
        
        try:
            response = self.client.session.post(url, json=data)
            if response.status_code == 201:
                print_success(f"Portfolio '{name}' generated")
                self.client.print_json(response.json())
                return response.json()
            else:
                print_error(f"Failed to generate portfolio: {response.status_code}")
                self.client.print_json(response.json())
                return None
        except Exception as e:
            print_error(f"Error: {str(e)}")
            return None
    
    def get_portfolio(self, portfolio_id: int):
        """Get detailed information about a portfolio"""
        url = f"{self.client.api_base}/portfolio/{portfolio_id}/"
        try:
            response = self.client.session.get(url)
            if response.status_code == 200:
                print_success(f"Portfolio {portfolio_id} details")
                self.client.print_json(response.json())
                return response.json()
            else:
                print_error(f"Failed to get portfolio: {response.status_code}")
                return None
        except Exception as e:
            print_error(f"Error: {str(e)}")
            return None
    
    def delete_portfolio(self, portfolio_id: int):
        """Delete a portfolio"""
        url = f"{self.client.api_base}/portfolio/{portfolio_id}/"
        try:
            response = self.client.session.delete(url)
            if response.status_code == 204:
                print_success(f"Portfolio {portfolio_id} deleted")
                return True
            else:
                print_error(f"Failed to delete portfolio: {response.status_code}")
                return False
        except Exception as e:
            print_error(f"Error: {str(e)}")
            return False
