#!/usr/bin/env python3
"""
Interactive API Terminal for Team 8 Capstone Project
A powerful command-line interface to interact with the backend API

Main entry point that orchestrates all command modules
"""
import os
import argparse
from .client import APIClient
from .commands.auth import AuthCommands
from .commands.user import UserCommands
from .commands.project import ProjectCommands
from .commands.portfolio import PortfolioCommands
from .commands.resume import ResumeCommands
from .commands.upload import UploadCommands
from .utils import Colors, print_header, print_info, print_error, print_warning


class APITerminal:
    """Interactive terminal for API communication"""
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        # Initialize client
        self.client = APIClient(base_url)
        
        # Initialize command handlers
        self.auth = AuthCommands(self.client)
        self.user = UserCommands(self.client)
        self.project = ProjectCommands(self.client)
        self.portfolio = PortfolioCommands(self.client)
        self.resume = ResumeCommands(self.client)
        self.upload = UploadCommands(self.client)
    
    def show_help(self):
        """Display help information"""
        print_header("API Terminal - Available Commands")
        
        commands = {
            "Authentication": [
                ("signup", "Register a new user account"),
                ("login", "Login with username and password"),
                ("logout", "Logout and clear tokens"),
                ("refresh", "Refresh access token"),
            ],
            "User Management": [
                ("whoami", "Get current user information"),
                ("user <username>", "Get public user profile"),
                ("passwd", "Change password"),
            ],
            "Projects": [
                ("projects", "List all projects"),
                ("project <id>", "Get project details"),
                ("upload <folder_path>", "Upload a folder as a new project"),
                ("upload-zip <zip_path>", "Upload a .zip file as a new project"),
                ("stats", "Get project statistics"),
                ("ranked", "Get ranked projects"),
                ("top", "Get top projects summary"),
                ("delete-project <id>", "Delete a project"),
            ],
            "Portfolios": [
                ("portfolios", "List all portfolios"),
                ("portfolio <id>", "Get portfolio details"),
                ("new-portfolio <name>", "Generate new portfolio"),
                ("delete-portfolio <id>", "Delete a portfolio"),
            ],
            "Resumes": [
                ("templates", "List resume templates"),
                ("new-resume", "Generate a new resume"),
                ("resume <id>", "Get resume details"),
            ],
            "Utilities": [
                ("schema", "Get API schema"),
                ("status", "Show connection and auth status"),
                ("help", "Show this help message"),
                ("clear", "Clear screen"),
                ("exit", "Exit the terminal"),
            ],
        }
        
        for category, cmds in commands.items():
            print(f"\n{Colors.CYAN}{Colors.BOLD}{category}:{Colors.ENDC}")
            for cmd, desc in cmds:
                print(f"  {Colors.GREEN}{cmd:30}{Colors.ENDC} {desc}")
        
        print()
    
    def show_status(self):
        """Show connection and authentication status"""
        print_header("Status")
        print(f"Base URL: {Colors.CYAN}{self.client.base_url}{Colors.ENDC}")
        print(f"API Base: {Colors.CYAN}{self.client.api_base}{Colors.ENDC}")
        
        if self.client.username:
            print(f"Logged in: {Colors.GREEN}Yes{Colors.ENDC} (as {Colors.BOLD}{self.client.username}{Colors.ENDC})")
            print(f"Access Token: {Colors.GREEN}Set{Colors.ENDC}")
            print(f"Refresh Token: {Colors.GREEN}Set{Colors.ENDC}")
        else:
            print(f"Logged in: {Colors.RED}No{Colors.ENDC}")
        print()
    
    def interactive_mode(self):
        """Run interactive command mode"""
        print_header("Team 8 Capstone API Terminal")
        print_info(f"Connected to: {self.client.base_url}")
        print_info("Type 'help' for available commands, 'exit' to quit")
        
        while True:
            try:
                # Show prompt
                if self.client.username:
                    prompt = f"{Colors.GREEN}{self.client.username}{Colors.ENDC}@api> "
                else:
                    prompt = f"{Colors.YELLOW}guest{Colors.ENDC}@api> "
                
                command = input(prompt).strip()
                
                if not command:
                    continue
                
                parts = command.split()
                cmd = parts[0].lower()
                args = parts[1:]
                
                # Handle commands
                if cmd in ['exit', 'quit', 'q']:
                    print_info("Goodbye!")
                    break
                
                elif cmd == 'help':
                    self.show_help()
                
                elif cmd == 'clear':
                    os.system('cls' if os.name == 'nt' else 'clear')
                
                elif cmd == 'status':
                    self.show_status()
                
                elif cmd == 'signup':
                    username = input("Username: ")
                    email = input("Email: ")
                    password = input("Password: ")
                    confirm_password = input("Confirm password: ")
                    first_name = input("First name (optional): ")
                    last_name = input("Last name (optional): ")
                    self.auth.signup(username, email, password, confirm_password, first_name, last_name)
                
                elif cmd == 'login':
                    username = input("Username: ")
                    password = input("Password: ")
                    self.auth.login(username, password)
                
                elif cmd == 'logout':
                    self.auth.logout()
                
                elif cmd == 'refresh':
                    self.auth.refresh_access_token()
                
                elif cmd == 'whoami':
                    self.user.get_current_user()
                
                elif cmd == 'user':
                    if args:
                        self.user.get_public_user(args[0])
                    else:
                        print_error("Usage: user <username>")
                
                elif cmd == 'passwd':
                    old_pass = input("Old password: ")
                    new_pass = input("New password: ")
                    self.user.change_password(old_pass, new_pass)
                
                elif cmd == 'projects':
                    self.project.list_projects()
                
                elif cmd == 'project':
                    if args:
                        self.project.get_project(int(args[0]))
                    else:
                        print_error("Usage: project <id>")
                
                elif cmd == 'stats':
                    self.project.get_project_stats()
                
                elif cmd == 'ranked':
                    self.project.get_ranked_projects()
                
                elif cmd == 'top':
                    self.project.get_top_projects_summary()
                
                elif cmd == 'upload':
                    if args:
                        path = ' '.join(args)
                        # Get consent
                        scan = input("Allow scanning? (y/n, default: y): ").strip().lower()
                        scan_consent = scan != 'n'
                        llm = input("Send to LLM for analysis? (y/n, default: y): ").strip().lower()
                        llm_consent = llm != 'n'
                        github = input("GitHub username (optional): ").strip()
                        # Auto-detect if zip or folder
                        if path.lower().endswith('.zip'):
                            self.upload.upload_zip(path, scan_consent, llm_consent, github)
                        else:
                            self.upload.upload_folder(path, scan_consent, llm_consent, github)
                    else:
                        print_error("Usage: upload <folder_path_or_zip>")
                
                elif cmd == 'upload-zip':
                    if args:
                        zip_path = ' '.join(args)
                        # Get consent
                        scan = input("Allow scanning? (y/n, default: y): ").strip().lower()
                        scan_consent = scan != 'n'
                        llm = input("Send to LLM for analysis? (y/n, default: y): ").strip().lower()
                        llm_consent = llm != 'n'
                        github = input("GitHub username (optional): ").strip()
                        self.upload.upload_zip(zip_path, scan_consent, llm_consent, github)
                    else:
                        print_error("Usage: upload-zip <zip_path>")
                
                elif cmd == 'delete-project':
                    if args:
                        self.project.delete_project(int(args[0]))
                    else:
                        print_error("Usage: delete-project <id>")
                
                elif cmd == 'portfolios':
                    self.portfolio.list_portfolios()
                
                elif cmd == 'portfolio':
                    if args:
                        self.portfolio.get_portfolio(int(args[0]))
                    else:
                        print_error("Usage: portfolio <id>")
                
                elif cmd == 'new-portfolio':
                    if args:
                        name = ' '.join(args)
                        desc = input("Description (optional): ")
                        self.portfolio.generate_portfolio(name, desc)
                    else:
                        print_error("Usage: new-portfolio <name>")
                
                elif cmd == 'delete-portfolio':
                    if args:
                        self.portfolio.delete_portfolio(int(args[0]))
                    else:
                        print_error("Usage: delete-portfolio <id>")
                
                elif cmd == 'templates':
                    self.resume.list_resume_templates()
                
                elif cmd == 'new-resume':
                    job_desc = input("Job description (optional): ")
                    self.resume.generate_resume(job_desc)
                
                elif cmd == 'resume':
                    if args:
                        self.resume.get_resume(int(args[0]))
                    else:
                        print_error("Usage: resume <id>")
                
                elif cmd == 'schema':
                    self.upload.get_api_schema()
                
                else:
                    print_error(f"Unknown command: {cmd}")
                    print_info("Type 'help' for available commands")
            
            except KeyboardInterrupt:
                print()
                print_info("Use 'exit' to quit")
            except Exception as e:
                print_error(f"Error: {str(e)}")


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description='Interactive API Terminal for Team 8 Capstone Project',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python -m terminal                    # Interactive mode (default)
  python -m terminal --url http://localhost:8000
  
Once in interactive mode, type 'help' to see available commands.
        """
    )
    
    parser.add_argument(
        '--url',
        default='http://localhost:8000',
        help='Base URL of the API (default: http://localhost:8000)'
    )
    
    args = parser.parse_args()
    
    # Create terminal instance
    terminal = APITerminal(base_url=args.url)
    
    # Run interactive mode
    terminal.interactive_mode()


if __name__ == '__main__':
    main()
