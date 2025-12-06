import unittest
from app.services.llm import ai_analyze


class TestAzureLLM(unittest.TestCase):
    """Simple tests for Azure OpenAI client"""

    def test_basic_completion(self):
        """Test that LLM returns a response"""
        prompt = "Say 'Hello' in one word."
        response = ai_analyze(prompt)
        
        self.assertIsNotNone(response)
        self.assertIsInstance(response, str)
        self.assertGreater(len(response), 0)
        print(f"\nLLM Response: {response}")

    def test_code_analysis(self):
        """Test LLM code analysis with default system message"""
        code = "def add(a, b): return a + b"
        prompt = f"Analyze this function: {code}"
        
        response = ai_analyze(prompt)
        
        self.assertIsNotNone(response)
        self.assertIsInstance(response, str)
        print(f"\nCode Analysis: {response[:200]}...")

    def test_resume_bullet_generation(self):
        """Test generating resume bullet points from code"""
        code_example = """
def authenticate_user(username, password):
    hashed = bcrypt.hash(password)
    if valid(username, hashed):
        return generate_jwt(username)
    return None
"""
        
        prompt = f"Generate 3 resume bullet points from this code:\n\n{code_example}"
        
        system_msg = """You are a resume writer. Generate ONLY bullet points in this exact format with no other text:

- point 1
- point 2  
- point 3

Do NOT include any introductions, explanations, or other text. ONLY the bullet points."""
        
        response = ai_analyze(prompt, system_message=system_msg)
        
        self.assertIsNotNone(response)
        self.assertIsInstance(response, str)
        self.assertIn("-", response)
        print(f"\nResume Bullet Points:\n{response}")


if __name__ == '__main__':
    unittest.main()
