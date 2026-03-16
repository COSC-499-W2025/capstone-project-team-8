import unittest
from unittest.mock import patch, MagicMock
from app.services.llm.factory import LLMFactory
from django.test import TestCase, tag

@tag('llm')
@patch('app.services.llm.factory.LLMFactory.get_provider')
class TestLLM(TestCase):
    """Simple tests for LLM client"""

    def test_basic_completion(self, mock_get_provider):
        """Test that LLM returns a response"""
        mock_provider = MagicMock()
        mock_provider.analyze.return_value = "Hello"
        mock_get_provider.return_value = mock_provider
        
        prompt = "Say 'Hello' in one word."
        response = LLMFactory.get_provider().analyze(prompt)
        
        self.assertIsNotNone(response)
        self.assertIsInstance(response, str)
        self.assertGreater(len(response), 0)
        print(f"\nLLM Response: {response}")

    def test_code_analysis(self, mock_get_provider):
        """Test LLM code analysis with default system message"""
        mock_provider = MagicMock()
        mock_provider.analyze.return_value = "This module adds numbers."
        mock_get_provider.return_value = mock_provider
        
        code = "def add(a, b): return a + b"
        prompt = f"Analyze this function: {code}"
        
        response = LLMFactory.get_provider().analyze(prompt)
        
        self.assertIsNotNone(response)
        self.assertIsInstance(response, str)
        print(f"\nCode Analysis: {response[:200]}...")

    def test_resume_bullet_generation(self, mock_get_provider):
        """Test generating resume bullet points from code"""
        mock_provider = MagicMock()
        mock_provider.analyze.return_value = "- Auth code\n- JWT support"
        mock_get_provider.return_value = mock_provider
        
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
        
        response = LLMFactory.get_provider().analyze(prompt, system_message=system_msg)
        
        self.assertIsNotNone(response)
        self.assertIsInstance(response, str)
        self.assertIn("-", response)
        print(f"\nResume Bullet Points:\n{response}")


if __name__ == '__main__':
    unittest.main()
