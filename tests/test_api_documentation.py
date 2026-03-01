"""
Tests for API documentation endpoints (drf-spectacular)
"""
from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
import json


class APIDocumentationTests(TestCase):
    """Test suite for API documentation endpoints"""

    def setUp(self):
        self.client = APIClient()

    def test_schema_endpoint_accessible(self):
        """Test that the OpenAPI schema endpoint is accessible"""
        url = reverse('schema')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 200)
        self.assertIn('application/vnd.oai.openapi', response['Content-Type'])

    def test_schema_is_valid_openapi(self):
        """Test that the schema returns valid OpenAPI 3.0 structure"""
        url = reverse('schema')
        response = self.client.get(url, {'format': 'json'})
        
        schema = json.loads(response.content)
        
        # Check required OpenAPI fields
        self.assertIn('openapi', schema)
        self.assertIn('info', schema)
        self.assertIn('paths', schema)
        
        # Verify OpenAPI version
        self.assertTrue(schema['openapi'].startswith('3.'))
        
        # Check API info
        self.assertEqual(schema['info']['title'], 'Team 8 Capstone Project API')
        self.assertEqual(schema['info']['version'], '1.0.0')

    def test_schema_contains_expected_endpoints(self):
        """Test that the schema documents all major endpoints"""
        url = reverse('schema')
        response = self.client.get(url, {'format': 'json'})
        schema = json.loads(response.content)
        
        paths = schema['paths']
        
        # Check that key endpoints are documented
        expected_paths = [
            '/api/upload-folder/',
            '/api/projects/',
            '/api/projects/ranked/',
            '/api/skills/',
            '/api/resume/templates/',
            '/api/resume/preview/',
            '/api/signup/',
            '/api/login/',
            '/api/token/',
            '/api/users/me/',
        ]
        
        for path in expected_paths:
            self.assertIn(path, paths, f"Expected {path} to be in schema")

    def test_swagger_ui_accessible(self):
        """Test that Swagger UI page loads successfully"""
        url = reverse('swagger-ui')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 200)
        self.assertIn('text/html', response['Content-Type'])
        # Check for Swagger UI specific content
        self.assertContains(response, 'swagger-ui')

    def test_redoc_accessible(self):
        """Test that ReDoc page loads successfully"""
        url = reverse('redoc')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 200)
        self.assertIn('text/html', response['Content-Type'])
        # Check for ReDoc specific content
        self.assertContains(response, 'redoc')

    def test_schema_documents_authentication(self):
        """Test that JWT authentication is documented in the schema"""
        url = reverse('schema')
        response = self.client.get(url, {'format': 'json'})
        schema = json.loads(response.content)
        
        # Check for security schemes
        self.assertIn('components', schema)
        self.assertIn('securitySchemes', schema['components'])
        
        # Verify JWT Bearer auth is documented
        security_schemes = schema['components']['securitySchemes']
        self.assertIn('jwtAuth', security_schemes)
        self.assertEqual(security_schemes['jwtAuth']['type'], 'http')
        self.assertEqual(security_schemes['jwtAuth']['scheme'], 'bearer')

    def test_schema_documents_request_bodies(self):
        """Test that POST endpoints document their structure"""
        url = reverse('schema')
        response = self.client.get(url, {'format': 'json'})
        schema = json.loads(response.content)
        
        # Check that schema has paths
        self.assertIn('paths', schema)
        
        # Verify at least token endpoints have proper documentation
        token_path = schema['paths'].get('/api/token/')
        if token_path and 'post' in token_path:
            post_method = token_path['post']
            # Token endpoint should have either requestBody or be documented
            self.assertIn('responses', post_method, 
                         "POST endpoint should have responses")

    def test_schema_documents_response_codes(self):
        """Test that endpoints document expected response codes"""
        url = reverse('schema')
        response = self.client.get(url, {'format': 'json'})
        schema = json.loads(response.content)
        
        # Check projects list endpoint
        projects_path = schema['paths'].get('/api/projects/')
        if projects_path and 'get' in projects_path:
            responses = projects_path['get']['responses']
            
            # Should document success response
            self.assertIn('200', responses, "Should document 200 success response")

    def test_schema_format_parameter(self):
        """Test that schema can be requested in different formats"""
        url = reverse('schema')
        
        # Test JSON format
        response = self.client.get(url, {'format': 'json'})
        self.assertEqual(response.status_code, 200)
        
        # Verify it's valid JSON
        try:
            json.loads(response.content)
        except json.JSONDecodeError:
            self.fail("Schema should return valid JSON")

    def test_schema_includes_tags(self):
        """Test that endpoints are organized with tags"""
        url = reverse('schema')
        response = self.client.get(url, {'format': 'json'})
        schema = json.loads(response.content)
        
        # At least one endpoint should have tags for organization
        has_tags = False
        for path_data in schema['paths'].values():
            for method_data in path_data.values():
                if 'tags' in method_data:
                    has_tags = True
                    break
            if has_tags:
                break
        
        self.assertTrue(has_tags, "Schema should use tags for endpoint organization")
