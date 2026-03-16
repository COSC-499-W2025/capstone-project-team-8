"""
Test LaTeX Resume Generator
"""
from django.test import TestCase
from django.contrib.auth import get_user_model
from app.models import Project, ProgrammingLanguage, Framework
from app.services.resume_builder.latex_generator import JakesResumeGenerator

User = get_user_model()


class LatexResumeGeneratorTests(TestCase):
    """Test LaTeX resume generation."""
    
    def setUp(self):
        """Set up test user and projects."""
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123',
            first_name='John',
            last_name='Doe',
            university='Test University',
            degree_major='Bachelor of Science in Computer Science',
            education_city='Vancouver',
            education_state='British Columbia'
        )
        
        # Create some languages and frameworks
        self.python = ProgrammingLanguage.objects.create(name='Python', category='general')
        self.javascript = ProgrammingLanguage.objects.create(name='JavaScript', category='web')
        self.django_fw = Framework.objects.create(name='Django', category='web_backend')
        self.react_fw = Framework.objects.create(name='React', category='web_frontend')
    
    def test_latex_resume_generation(self):
        """Test generating LaTeX resume with basic user data."""
        generator = JakesResumeGenerator(self.user)
        latex_content = generator.generate()
        
        # Check that content is generated
        self.assertIsNotNone(latex_content)
        self.assertIsInstance(latex_content, str)
        self.assertGreater(len(latex_content), 100)
        
        # Check for LaTeX document structure
        self.assertIn(r'\documentclass', latex_content)
        self.assertIn(r'\begin{document}', latex_content)
        self.assertIn(r'\end{document}', latex_content)
        
        # Check for user information
        self.assertIn('John Doe', latex_content)
        self.assertIn('test@example.com', latex_content)
        
    def test_latex_resume_with_education(self):
        """Test that education fields are included in resume."""
        generator = JakesResumeGenerator(self.user)
        latex_content = generator.generate()
        
        # Check education section
        self.assertIn(r'\section{Education}', latex_content)
        self.assertIn('Test University', latex_content)
        self.assertIn('Computer Science', latex_content)
        self.assertIn('Vancouver', latex_content)
        self.assertIn('British Columbia', latex_content)
    
    def test_latex_resume_with_projects(self):
        """Test that projects are included in resume."""
        # Create a test project
        project = Project.objects.create(
            user=self.user,
            name='Test Project',
            description='A test project for resume generation',
            classification_type='coding',
            resume_bullet_points=['Built a web application', 'Deployed to production']
        )
        project.languages.add(self.python, self.javascript)
        project.frameworks.add(self.django_fw, self.react_fw)
        
        generator = JakesResumeGenerator(self.user)
        latex_content = generator.generate()
        
        # Check projects section
        self.assertIn(r'\section{Projects}', latex_content)
        self.assertIn('Test Project', latex_content)
        self.assertIn('Built a web application', latex_content)
    
    def test_latex_resume_with_skills(self):
        """Test that skills are extracted from projects."""
        # Create a project with languages and frameworks
        project = Project.objects.create(
            user=self.user,
            name='Fullstack App',
            classification_type='coding'
        )
        project.languages.add(self.python, self.javascript)
        project.frameworks.add(self.django_fw, self.react_fw)
        
        generator = JakesResumeGenerator(self.user)
        latex_content = generator.generate()
        
        # Check skills section
        self.assertIn(r'\section{Technical Skills}', latex_content)
        self.assertIn('Python', latex_content)
        self.assertIn('JavaScript', latex_content)
        self.assertIn('Django', latex_content)
        self.assertIn('React', latex_content)
    
    def test_latex_special_character_escaping(self):
        """Test that special LaTeX characters are escaped."""
        # Create a project with special characters
        project = Project.objects.create(
            user=self.user,
            name='C++ & Python Project',
            description='Built with $100 budget & 50% improvement',
            classification_type='coding',
            resume_bullet_points=['Reduced costs by 50% using C++', 'Implemented API & backend']
        )
        
        generator = JakesResumeGenerator(self.user)
        latex_content = generator.generate()
        
        # Check that special characters in user content are escaped
        self.assertIn(r'C++ \& Python Project', latex_content)  # & should be \&
        self.assertIn(r'\$100', latex_content)  # $ should be \$
        self.assertIn(r'50\%', latex_content)  # % should be \%


if __name__ == '__main__':
    import unittest
    unittest.main()
