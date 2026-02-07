"""
Upload command handlers
Handles uploading zip files and folders for project analysis
"""
import os
import zipfile
import tempfile
from pathlib import Path
from ..client import APIClient
from ..utils import print_success, print_error, print_info


class UploadCommands:
    """Upload management commands"""
    
    def __init__(self, client: APIClient):
        self.client = client
    
    def upload_zip(self, zip_path: str, scan_consent: bool = True, 
                   llm_consent: bool = True, github_username: str = ""):
        """Upload a zip file for analysis"""
        url = f"{self.client.api_base}/upload-folder/"
        
        # Validate zip exists
        if not os.path.exists(zip_path):
            print_error(f"File not found: {zip_path}")
            return None
        
        if not zip_path.lower().endswith('.zip'):
            print_error(f"File must be a .zip file: {zip_path}")
            return None
        
        print_info(f"Preparing to upload: {zip_path}")
        
        try:
            # Upload the zip file
            print_info("Uploading to server...")
            with open(zip_path, 'rb') as f:
                files = {'file': (os.path.basename(zip_path), f, 'application/zip')}
                data = {
                    'consent_scan': str(scan_consent).lower(),
                    'consent_send_llm': str(llm_consent).lower(),
                }
                if github_username:
                    data['github_username'] = github_username
                
                response = self.client.session.post(url, files=files, data=data)
            
            if response.status_code == 200:
                print_success("Zip file uploaded and analyzed successfully!")
                result = response.json()
                self.client.print_json(result)
                return result
            else:
                print_error(f"Upload failed: {response.status_code}")
                try:
                    self.client.print_json(response.json())
                except:
                    print(response.text)
                return None
                
        except Exception as e:
            print_error(f"Upload error: {str(e)}")
            import traceback
            traceback.print_exc()
            return None
    
    def upload_folder(self, folder_path: str, scan_consent: bool = True, 
                      llm_consent: bool = True, github_username: str = ""):
        """Upload a folder for analysis"""
        url = f"{self.client.api_base}/upload-folder/"
        
        # Validate folder exists
        if not os.path.exists(folder_path):
            print_error(f"Folder not found: {folder_path}")
            return None
        
        if not os.path.isdir(folder_path):
            print_error(f"Path is not a directory: {folder_path}")
            return None
        
        print_info(f"Preparing to upload: {folder_path}")
        
        try:
            # Create a temporary zip file
            with tempfile.NamedTemporaryFile(suffix='.zip', delete=False) as tmp_zip:
                zip_path = tmp_zip.name
            
            # Zip the folder
            print_info("Creating zip file...")
            with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                folder = Path(folder_path)
                for file_path in folder.rglob('*'):
                    if file_path.is_file():
                        arcname = file_path.relative_to(folder.parent)
                        zipf.write(file_path, arcname)
                        print(f"  Adding: {arcname}")
            
            print_success(f"Zip created: {zip_path}")
            
            # Upload the zip file
            print_info("Uploading to server...")
            with open(zip_path, 'rb') as f:
                files = {'file': (os.path.basename(folder_path) + '.zip', f, 'application/zip')}
                data = {
                    'consent_scan': str(scan_consent).lower(),
                    'consent_send_llm': str(llm_consent).lower(),
                }
                if github_username:
                    data['github_username'] = github_username
                
                response = self.client.session.post(url, files=files, data=data)
            
            # Clean up temp file
            os.unlink(zip_path)
            
            if response.status_code == 200:
                print_success("Folder uploaded and analyzed successfully!")
                result = response.json()
                self.client.print_json(result)
                return result
            else:
                print_error(f"Upload failed: {response.status_code}")
                try:
                    self.client.print_json(response.json())
                except:
                    print(response.text)
                return None
                
        except Exception as e:
            print_error(f"Upload error: {str(e)}")
            import traceback
            traceback.print_exc()
            return None
    
    def get_api_schema(self):
        """Get OpenAPI schema"""
        url = f"{self.client.api_base}/schema/"
        try:
            response = self.client.session.get(url, params={'format': 'json'})
            if response.status_code == 200:
                print_success("API Schema retrieved")
                schema = response.json()
                # Print just the info and paths overview
                from ..utils import Colors
                print(f"\n{Colors.BOLD}API Information:{Colors.ENDC}")
                self.client.print_json(schema.get('info', {}))
                print(f"\n{Colors.BOLD}Available Endpoints ({len(schema.get('paths', {}))} total):{Colors.ENDC}")
                for path in sorted(schema.get('paths', {}).keys()):
                    print(f"  • {path}")
                return schema
            else:
                print_error(f"Failed to get schema: {response.status_code}")
                return None
        except Exception as e:
            print_error(f"Error: {str(e)}")
            return None
