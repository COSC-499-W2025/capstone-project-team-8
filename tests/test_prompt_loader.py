"""
Tests the prompt_loader utility functions to ensure they work correctly
for loading, parsing, and building prompts from markdown templates.

Run with: python -m pytest test_prompt_loader.py -v
Or: python test_prompt_loader.py
"""

import sys
import os
import unittest
from pathlib import Path

# Add the correct path to find the app module
project_root = Path(__file__).parent.parent
backend_path = project_root / "src" / "backend"
sys.path.insert(0, str(backend_path))

from app.utils.prompt_loader import (
    get_available_templates,
    load_prompt_template,
    build_prompt,
    search_templates,
    get_templates_by_category,
    get_all_categories,
    PromptTemplate
)


class TestPromptLoader(unittest.TestCase):
    """Test cases for prompt loader utility functions."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.known_template = "improvement_best_practice_analysis"
        self.sample_context = "Focus on Python security and performance"
    
    def test_get_available_templates(self):
        """Test getting list of available templates."""
        templates = get_available_templates()
        
        # Should return a list
        self.assertIsInstance(templates, list)
        
        # Should have templates (we know there are 70+)
        self.assertGreater(len(templates), 50, "Should have many templates")
        
        # Should be sorted
        self.assertEqual(templates, sorted(templates), "Templates should be sorted")
        
        # Should contain known template
        self.assertIn(self.known_template, templates)
        
        # All should be strings without .md extension
        for template in templates:
            self.assertIsInstance(template, str)
            self.assertFalse(template.endswith('.md'))
    
    def test_load_prompt_template_success(self):
        """Test successfully loading a template."""
        template = load_prompt_template(self.known_template)
        
        # Should return PromptTemplate object
        self.assertIsInstance(template, PromptTemplate)
        
        # Should have correct name
        self.assertEqual(template.name, self.known_template)
        
        # Should have content in all sections
        self.assertGreater(len(template.objective), 0, "Should have objective")
        self.assertGreater(len(template.instructions), 0, "Should have instructions")
        self.assertGreater(len(template.expected_output), 0, "Should have expected output")
        self.assertGreater(len(template.full_content), 0, "Should have full content")
        
        # Objective should be a clear sentence
        self.assertIn("analyze", template.objective.lower())
        
        # Instructions should contain numbered steps
        self.assertTrue(any(char.isdigit() for char in template.instructions))
        
    def test_load_prompt_template_not_found(self):
        """Test loading non-existent template."""
        with self.assertRaises(FileNotFoundError):
            load_prompt_template("nonexistent_template")
    
    def test_build_prompt_with_context(self):
        """Test building a complete prompt with user context."""
        prompt = build_prompt(self.known_template, self.sample_context)
        
        # Should return a string
        self.assertIsInstance(prompt, str)
        
        # Should have substantial content
        self.assertGreater(len(prompt), 100, "Prompt should be substantial")
        
        # Should contain key sections
        self.assertIn("Objective:", prompt)
        self.assertIn("Instructions:", prompt)
        self.assertIn("Expected Output:", prompt)
        
        # Should contain user context
        self.assertIn(self.sample_context, prompt)
        
        # Should contain template content
        template = load_prompt_template(self.known_template)
        self.assertIn(template.objective, prompt)
    
    def test_build_prompt_without_context(self):
        """Test building prompt without additional context."""
        prompt = build_prompt(self.known_template)
        
        # Should still work
        self.assertIsInstance(prompt, str)
        self.assertGreater(len(prompt), 50)
        
        # Should contain template sections
        self.assertIn("Objective:", prompt)
        self.assertIn("Instructions:", prompt)

    def test_search_templates_no_results(self):
        """Test searching with term that has no results."""
        results = search_templates("xyznoresultsexpected")
        self.assertIsInstance(results, list)
        self.assertEqual(len(results), 0)
    
    def test_get_templates_by_category(self):
        """Test getting templates by category."""
        # Test known categories
        code_analysis = get_templates_by_category("code_analysis")
        testing = get_templates_by_category("testing")
        
        # Should return lists
        self.assertIsInstance(code_analysis, list)
        self.assertIsInstance(testing, list)
        
        # Should have templates
        self.assertGreater(len(code_analysis), 0, "Code analysis category should have templates")
        
        # Should contain expected templates
        expected_code_templates = [
            "learning_frontend_code_analysis",
            "learning_backend_code_analysis", 
            "improvement_best_practice_analysis"
        ]
        
        for expected in expected_code_templates:
            self.assertIn(expected, code_analysis, f"Should contain {expected}")
    
    def test_get_templates_by_unknown_category(self):
        """Test getting templates for unknown category."""
        result = get_templates_by_category("unknown_category")
        self.assertIsInstance(result, list)
        self.assertEqual(len(result), 0)
    
    def test_get_all_categories(self):
        """Test getting all available categories."""
        categories = get_all_categories()
        
        # Should return dict
        self.assertIsInstance(categories, dict)
        
        # Should have expected categories
        expected_categories = [
            "code_analysis", 
            "testing", 
            "refactoring", 
            "business_analysis",
            "architecture", 
            "performance"
        ]
        
        for category in expected_categories:
            self.assertIn(category, categories, f"Should have {category} category")
            self.assertIsInstance(categories[category], list)
    
    def test_prompt_template_to_dict(self):
        """Test PromptTemplate to_dict method."""
        template = load_prompt_template(self.known_template)
        template_dict = template.to_dict()
        
        # Should return dict
        self.assertIsInstance(template_dict, dict)
        
        # Should have expected keys
        expected_keys = ["name", "objective", "instructions", "expected_output", "full_content"]
        for key in expected_keys:
            self.assertIn(key, template_dict)
        
        # Values should match template attributes
        self.assertEqual(template_dict["name"], template.name)
        self.assertEqual(template_dict["objective"], template.objective)
    
    def test_prompt_template_build_prompt_method(self):
        """Test PromptTemplate build_prompt method."""
        template = load_prompt_template(self.known_template)
        
        # Test with context
        prompt_with_context = template.build_prompt(self.sample_context)
        self.assertIn(self.sample_context, prompt_with_context)
        
        # Test without context
        prompt_without_context = template.build_prompt()
        self.assertNotIn(self.sample_context, prompt_without_context)
        
        # Both should have template content
        self.assertIn(template.objective, prompt_with_context)
        self.assertIn(template.objective, prompt_without_context)
    
    def test_integration_realistic_workflow(self):
        """Test a realistic end-to-end workflow."""
        # 1. User searches for templates
        search_results = search_templates("frontend")
        self.assertGreater(len(search_results), 0)
        
        # 2. User picks a template
        frontend_template = "learning_frontend_code_analysis"
        self.assertIn(frontend_template, search_results)
        
        # 3. User builds prompt with context
        user_context = "Analyze React components for performance issues and accessibility"
        prompt = build_prompt(frontend_template, user_context)
        
        # 4. Verify prompt is ready for API
        self.assertIsInstance(prompt, str)
        self.assertIn("React", prompt)  # User context included
        self.assertIn("frontend", prompt.lower())  # Template content included
        self.assertGreater(len(prompt), 200)  # Substantial content
        
        print(f"\n✅ Integration test passed!")
        print(f"   Template: {frontend_template}")
        print(f"   Context: {user_context}")
        print(f"   Prompt length: {len(prompt)} characters")


def run_manual_tests():
    """Run some manual verification tests."""
    print("🧪 Manual Verification Tests")
    print("=" * 50)
    
    # Test 1: List templates
    templates = get_available_templates()
    print(f"✅ Found {len(templates)} templates")
    print(f"   First 5: {templates[:5]}")
    
    # Test 2: Load and inspect template
    template = load_prompt_template("improvement_best_practice_analysis")
    print(f"\n✅ Loaded template: {template.name}")
    print(f"   Objective: {template.objective[:50]}...")
    print(f"   Instructions length: {len(template.instructions)} chars")
    
    # Test 3: Build prompt
    prompt = build_prompt("testing_unit_test_generation", "Focus on edge cases")
    print(f"\n✅ Built prompt: {len(prompt)} characters")
    print(f"   Contains 'edge cases': {'edge cases' in prompt}")
    
    # Test 4: Search functionality
    results = search_templates("performance")
    print(f"\n✅ Search for 'performance' found {len(results)} results")
    if results:
        print(f"   Examples: {results[:3]}")
    
    print("\n🎉 All manual tests completed!")


if __name__ == "__main__":
    print("🚀 Running Prompt Loader Tests")
    print("=" * 60)
    
    # Run unittest suite
    unittest.main(argv=[''], exit=False, verbosity=2)
    
    # Run manual verification
    print("\n" + "=" * 60)
    run_manual_tests()