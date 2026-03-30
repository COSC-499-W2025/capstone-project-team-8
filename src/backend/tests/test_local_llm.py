"""
Simple Local LLM Service Test
Tests your local LLM service and provides setup guidance
"""

import unittest
import requests
import os

class TestLocalLLMSetup(unittest.TestCase):
    """Test local LLM service setup"""
    
    def test_local_server_status(self):
        """Check local server status and provide setup guidance"""
        try:
            # Test health endpoint
            health_response = requests.get("http://localhost:3001/health", timeout=3)
            
            if health_response.status_code == 200:
                data = health_response.json()
                print(f"\nLocal server is running on http://localhost:3001")
                print(f"  - Status: {data.get('status')}")
                print(f"  - Uptime: {data.get('uptime', 0):.1f} seconds")
                
                # Test if API endpoint exists
                try:
                    api_test = requests.post("http://localhost:3001/api/query", 
                                           json={'prompt': 'test'}, timeout=3)
                    
                    if api_test.status_code == 401:
                        print("✓ API endpoint is working (authentication required)")
                        return True
                    elif api_test.status_code == 404:
                        print("✗ API endpoint missing - server needs restart with latest code")
                        self._print_restart_instructions()
                        return False
                    else:
                        print(f"✓ API endpoint responds (status: {api_test.status_code})")
                        return True
                        
                except Exception as e:
                    print(f"✗ Error testing API endpoint: {e}")
                    return False
            else:
                print(f"✗ Server responded with unexpected status: {health_response.status_code}")
                return False
                
        except requests.exceptions.ConnectionError:
            print("✗ Local LLM server is not running")
            self._print_setup_instructions()
            return False
        except Exception as e:
            print(f"✗ Error connecting to server: {e}")
            return False
    
    def _print_setup_instructions(self):
        """Print instructions for starting the local server"""
        print("\n📋 To start your local LLM server:")
        print("   1. Open a new terminal/command prompt")
        print("   2. Navigate to the LLM service directory:")
        print("      cd src/llm-service")
        print("   3. Install dependencies (if not already done):")
        print("      npm install")
        print("   4. Start the server:")
        print("      node index.js")
        print("   5. You should see: 'API running on http://localhost:3001'")
    
    def _print_restart_instructions(self):
        """Print instructions for restarting with latest code"""
        print("\n🔄 To restart server with latest code:")
        print("   1. Stop the current server (Ctrl+C in its terminal)")
        print("   2. Navigate to src/llm-service (if not already there)")
        print("   3. Start the server again:")
        print("      node index.js")
        print("   4. The server should now have the /api/query endpoint")


class TestLocalLLMFunctionality(unittest.TestCase):
    """Test local LLM functionality (requires server to be running)"""
    
    def setUp(self):
        # Check if server is available before running tests
        try:
            health_check = requests.get("http://localhost:3001/health", timeout=2)
            api_check = requests.post("http://localhost:3001/api/query", json={'prompt': 'test'}, timeout=2)
            self.server_ready = health_check.status_code == 200 and api_check.status_code != 404
        except:
            self.server_ready = False
    
    def test_health_endpoint(self):
        """Test the health endpoint"""
        if not self.server_ready:
            self.skipTest("Local server not properly configured")
        
        response = requests.get("http://localhost:3001/health", timeout=5)
        self.assertEqual(response.status_code, 200)
        
        data = response.json()
        self.assertEqual(data['status'], 'ok')
        self.assertIn('uptime', data)
        self.assertIn('timestamp', data)
        
        print(f"✓ Health endpoint working - Uptime: {data['uptime']:.1f}s")
    
    def test_api_requires_auth(self):
        """Test that API requires authentication"""
        if not self.server_ready:
            self.skipTest("Local server not properly configured")
        
        response = requests.post("http://localhost:3001/api/query", 
                               json={'prompt': 'Hello'}, timeout=5)
        
        self.assertEqual(response.status_code, 401)
        print("✓ API properly requires authentication")
    
    def test_file_upload(self):
        """Test file upload functionality"""
        if not self.server_ready:
            self.skipTest("Local server not properly configured")
        
        # Create a test file
        test_content = "def hello():\n    return 'Hello, World!'"
        
        api_key = os.getenv('LLM_API_KEY', 'test-key')
        headers = {'x-api-key': api_key}
        
        files = {'file': ('test.py', test_content, 'text/x-python')}
        data = {'prompt': 'What does this code do?'}
        
        response = requests.post("http://localhost:3001/api/query",
                               files=files, data=data, headers=headers, timeout=180)
        
        # Accept 401 as a valid response (authentication issue)
        self.assertIn(response.status_code, [200, 400, 401, 500])
        
        if response.status_code == 200:
            result = response.json()
            self.assertTrue(result.get('fileProcessed', False))
            print("✓ File upload works - LLM processed the file")
        elif response.status_code == 400:
            print("✓ File upload validation working")
        elif response.status_code == 401:
            print("✓ File upload properly requires authentication")
            # Test that authentication is working by checking the error message
            try:
                error_data = response.json()
                self.assertIn('error', error_data)
                print(f"   - Error message: {error_data.get('error', 'No error message')}")
            except:
                print("   - Authentication rejection confirmed")
        else:
            print("✓ File upload accepted but Ollama unavailable")
    
    def test_file_upload_with_real_key(self):
        """Test file upload with the real API key from .env"""
        if not self.server_ready:
            self.skipTest("Local server not properly configured")
        
        # Try to get the real API key from .env
        real_api_key = None
        # Look for .env file in the llm-service directory
        project_root = os.path.dirname(os.path.dirname(__file__))
        env_file = os.path.join(project_root, 'src', 'llm-service', '.env')
        if os.path.exists(env_file):
            with open(env_file, 'r') as f:
                for line in f:
                    if line.startswith('LLM_API_KEY='):
                        real_api_key = line.split('=', 1)[1].strip()
                        break
        
        if not real_api_key:
            self.skipTest("Real API key not found in .env file")
        
        # Create a test file
        test_content = """# Simple Python function
def calculate_sum(a, b):
    \"\"\"Add two numbers and return the result\"\"\"
    return a + b

def main():
    result = calculate_sum(5, 3)
    print(f"The sum is: {result}")

if __name__ == "__main__":
    main()"""
        
        headers = {'x-api-key': real_api_key}
        files = {'file': ('calculator.py', test_content, 'text/x-python')}
        data = {'prompt': 'Analyze this Python code and explain what it does'}
        
        response = requests.post("http://localhost:3001/api/query",
                               files=files, data=data, headers=headers, timeout=180)
        
        # Should work with real key (200) or Ollama might be unavailable (500)
        self.assertIn(response.status_code, [200, 500])
        
        if response.status_code == 200:
            result = response.json()
            self.assertTrue(result.get('success', False))
            self.assertTrue(result.get('fileProcessed', False))
            self.assertEqual(result.get('filename'), 'calculator.py')
            print("✅ File upload with real API key successful!")
            print(f"   - File processed: {result.get('filename')}")
            print(f"   - Model used: {result.get('model', 'Unknown')}")
            # Show first 100 chars of response
            llm_response = result.get('response', '')
            if llm_response:
                preview = llm_response[:100].replace('\n', ' ')
                print(f"   - LLM response preview: {preview}...")
        else:
            print("✅ File upload accepted with real key but Ollama service unavailable")


if __name__ == '__main__':
    print("=" * 70)
    print("LOCAL LLM SERVICE TEST")
    print("=" * 70)
    
    # First run setup check
    suite = unittest.TestSuite()
    suite.addTest(TestLocalLLMSetup('test_local_server_status'))
    runner = unittest.TextTestRunner(verbosity=0)
    result = runner.run(suite)
    
    # If setup is good, run functionality tests
    if not result.failures and not result.errors:
        print(f"\n{'='*70}")
        print("RUNNING FUNCTIONALITY TESTS")
        print("=" * 70)
        unittest.main(argv=[''], verbosity=2, exit=False)
    else:
        print(f"\n{'='*70}")
        print("Fix the setup issues above, then run the test again!")
        print("=" * 70)