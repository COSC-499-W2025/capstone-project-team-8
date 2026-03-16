"""
Tests for Skills Endpoint

Tests the GET /api/skills/ endpoint that aggregates skills
(languages and frameworks) from a user's projects.
"""
from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework.test import APIClient
from app.models import Project, ProgrammingLanguage, Framework, ProjectLanguage, ProjectFramework

User = get_user_model()


class SkillsEndpointTests(TestCase):
    """Test suite for the skills aggregation endpoint"""
    
    def setUp(self):
        """Set up test client and user"""
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='pass123'
        )
        self.url = '/api/skills/'
    
    def test_skills_endpoint_requires_authentication(self):
        """Test that unauthenticated users cannot access the endpoint"""
        response = self.client.get(self.url)
        self.assertIn(response.status_code, [401, 403])
    
    def test_skills_endpoint_empty_for_user_with_no_projects(self):
        """Test that endpoint returns empty lists for users with no projects"""
        self.client.force_authenticate(user=self.user)
        response = self.client.get(self.url)
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        
        self.assertIn('languages', data)
        self.assertIn('frameworks', data)
        self.assertEqual(data['languages'], [])
        self.assertEqual(data['frameworks'], [])
        self.assertEqual(data['total_projects'], 0)
    
    def test_skills_endpoint_returns_aggregated_skills(self):
        """Test that endpoint returns all languages and frameworks from user projects"""
        self.client.force_authenticate(user=self.user)
        
        # Create programming languages and frameworks
        python = ProgrammingLanguage.objects.create(name='Python')
        javascript = ProgrammingLanguage.objects.create(name='JavaScript')
        react = Framework.objects.create(name='React')
        django_fw = Framework.objects.create(name='Django')
        
        # Create projects
        project1 = Project.objects.create(
            user=self.user,
            name='Web App',
            classification_type='coding'
        )
        project2 = Project.objects.create(
            user=self.user,
            name='Frontend Project',
            classification_type='coding'
        )
        
        # Associate languages and frameworks with projects
        ProjectLanguage.objects.create(project=project1, language=python, file_count=10)
        ProjectLanguage.objects.create(project=project2, language=javascript, file_count=8)
        ProjectFramework.objects.create(project=project1, framework=django_fw)
        ProjectFramework.objects.create(project=project2, framework=react)
        
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        
        data = response.json()
        
        # Verify structure
        self.assertIn('languages', data)
        self.assertIn('frameworks', data)
        self.assertIn('total_projects', data)
        
        # Check languages
        language_names = [lang['name'] for lang in data['languages']]
        self.assertIn('Python', language_names)
        self.assertIn('JavaScript', language_names)
        
        # Check frameworks
        framework_names = [fw['name'] for fw in data['frameworks']]
        self.assertIn('React', framework_names)
        self.assertIn('Django', framework_names)
        
        # Check total projects
        self.assertEqual(data['total_projects'], 2)
    
    def test_skills_include_project_counts(self):
        """Test that skills include count of projects using them"""
        self.client.force_authenticate(user=self.user)
        
        # Create skills
        python = ProgrammingLanguage.objects.create(name='Python')
        javascript = ProgrammingLanguage.objects.create(name='JavaScript')
        django_fw = Framework.objects.create(name='Django')
        
        # Create 3 projects, 2 use Python, 1 uses JavaScript
        project1 = Project.objects.create(user=self.user, name='Project 1', classification_type='coding')
        project2 = Project.objects.create(user=self.user, name='Project 2', classification_type='coding')
        project3 = Project.objects.create(user=self.user, name='Project 3', classification_type='coding')
        
        # Python in projects 1 and 2
        ProjectLanguage.objects.create(project=project1, language=python, file_count=5)
        ProjectLanguage.objects.create(project=project2, language=python, file_count=3)
        
        # JavaScript in project 3
        ProjectLanguage.objects.create(project=project3, language=javascript, file_count=4)
        
        # Django in project 1
        ProjectFramework.objects.create(project=project1, framework=django_fw)
        
        response = self.client.get(self.url)
        data = response.json()
        
        # Find Python and verify count
        python_skill = next((s for s in data['languages'] if s['name'] == 'Python'), None)
        self.assertIsNotNone(python_skill)
        self.assertEqual(python_skill['project_count'], 2)
        
        # Find JavaScript and verify count
        js_skill = next((s for s in data['languages'] if s['name'] == 'JavaScript'), None)
        self.assertIsNotNone(js_skill)
        self.assertEqual(js_skill['project_count'], 1)
        
        # Find Django and verify count
        django_skill = next((s for s in data['frameworks'] if s['name'] == 'Django'), None)
        self.assertIsNotNone(django_skill)
        self.assertEqual(django_skill['project_count'], 1)
    
    def test_skills_sorted_by_project_count(self):
        """Test that skills are sorted by project_count (most used first)"""
        self.client.force_authenticate(user=self.user)
        
        # Create skills
        python = ProgrammingLanguage.objects.create(name='Python')
        javascript = ProgrammingLanguage.objects.create(name='JavaScript')
        java = ProgrammingLanguage.objects.create(name='Java')
        
        # Create projects
        p1 = Project.objects.create(user=self.user, name='P1', classification_type='coding')
        p2 = Project.objects.create(user=self.user, name='P2', classification_type='coding')
        p3 = Project.objects.create(user=self.user, name='P3', classification_type='coding')
        p4 = Project.objects.create(user=self.user, name='P4', classification_type='coding')
        
        # Python in 3 projects (most)
        ProjectLanguage.objects.create(project=p1, language=python, file_count=5)
        ProjectLanguage.objects.create(project=p2, language=python, file_count=5)
        ProjectLanguage.objects.create(project=p3, language=python, file_count=5)
        
        # JavaScript in 2 projects
        ProjectLanguage.objects.create(project=p2, language=javascript, file_count=3)
        ProjectLanguage.objects.create(project=p4, language=javascript, file_count=3)
        
        # Java in 1 project (least)
        ProjectLanguage.objects.create(project=p1, language=java, file_count=2)
        
        response = self.client.get(self.url)
        data = response.json()
        
        languages = data['languages']
        self.assertEqual(len(languages), 3)
        
        # Check order: Python (3) -> JavaScript (2) -> Java (1)
        self.assertEqual(languages[0]['name'], 'Python')
        self.assertEqual(languages[0]['project_count'], 3)
        self.assertEqual(languages[1]['name'], 'JavaScript')
        self.assertEqual(languages[1]['project_count'], 2)
        self.assertEqual(languages[2]['name'], 'Java')
        self.assertEqual(languages[2]['project_count'], 1)
    
    def test_skills_scoped_to_authenticated_user(self):
        """Test that skills are only from the authenticated user's projects"""
        self.client.force_authenticate(user=self.user)
        
        # Create another user with different skills
        other_user = User.objects.create_user(
            username='otheruser',
            email='other@example.com',
            password='pass123'
        )
        
        # Create skills
        python = ProgrammingLanguage.objects.create(name='Python')
        ruby = ProgrammingLanguage.objects.create(name='Ruby')
        
        # Current user has Python project
        user_project = Project.objects.create(user=self.user, name='My Project', classification_type='coding')
        ProjectLanguage.objects.create(project=user_project, language=python, file_count=5)
        
        # Other user has Ruby project
        other_project = Project.objects.create(user=other_user, name='Other Project', classification_type='coding')
        ProjectLanguage.objects.create(project=other_project, language=ruby, file_count=5)
        
        response = self.client.get(self.url)
        data = response.json()
        
        # Should only see Python (current user's skill), not Ruby
        language_names = [lang['name'] for lang in data['languages']]
        self.assertIn('Python', language_names)
        self.assertNotIn('Ruby', language_names)
        self.assertEqual(len(data['languages']), 1)

    # ------------------------------------------------------------------ #
    #  resume_skills tests                                                 #
    # ------------------------------------------------------------------ #

    def test_resume_skills_present_in_response(self):
        """Test that endpoint response includes a resume_skills key"""
        self.client.force_authenticate(user=self.user)
        response = self.client.get(self.url)
        data = response.json()
        self.assertIn('resume_skills', data)

    def test_resume_skills_empty_for_user_with_no_projects(self):
        """resume_skills should be an empty list when user has no projects"""
        self.client.force_authenticate(user=self.user)
        response = self.client.get(self.url)
        data = response.json()
        self.assertEqual(data['resume_skills'], [])

    def test_resume_skills_returned_from_projects(self):
        """Test that resume_skills stored on projects are surfaced by the endpoint"""
        self.client.force_authenticate(user=self.user)

        Project.objects.create(
            user=self.user,
            name='Writing Project',
            classification_type='writing',
            resume_skills=['Creative Writing', 'Technical Writing']
        )
        Project.objects.create(
            user=self.user,
            name='Art Project',
            classification_type='art',
            resume_skills=['Photography', 'Photo Editing']
        )

        response = self.client.get(self.url)
        data = response.json()

        skill_names = [s['name'] for s in data['resume_skills']]
        self.assertIn('Creative Writing', skill_names)
        self.assertIn('Technical Writing', skill_names)
        self.assertIn('Photography', skill_names)
        self.assertIn('Photo Editing', skill_names)

    def test_resume_skills_include_project_counts(self):
        """Each resume skill entry must carry the number of projects that have it"""
        self.client.force_authenticate(user=self.user)

        for i in range(3):
            Project.objects.create(
                user=self.user,
                name=f'Project {i}',
                classification_type='writing',
                resume_skills=['Technical Writing', 'Documentation']
            )
        Project.objects.create(
            user=self.user,
            name='Solo Project',
            classification_type='writing',
            resume_skills=['Technical Writing']
        )

        response = self.client.get(self.url)
        data = response.json()

        tw = next(s for s in data['resume_skills'] if s['name'] == 'Technical Writing')
        doc = next(s for s in data['resume_skills'] if s['name'] == 'Documentation')

        self.assertEqual(tw['project_count'], 4)
        self.assertEqual(doc['project_count'], 3)

    def test_resume_skills_sorted_by_project_count(self):
        """resume_skills must be sorted most-used first"""
        self.client.force_authenticate(user=self.user)

        for _ in range(3):
            Project.objects.create(
                user=self.user, name='P', classification_type='writing',
                resume_skills=['Technical Writing']
            )
        for _ in range(2):
            Project.objects.create(
                user=self.user, name='P', classification_type='writing',
                resume_skills=['Documentation']
            )
        Project.objects.create(
            user=self.user, name='P', classification_type='art',
            resume_skills=['Photography']
        )

        response = self.client.get(self.url)
        skills = response.json()['resume_skills']

        counts = [s['project_count'] for s in skills]
        self.assertEqual(counts, sorted(counts, reverse=True))
        self.assertEqual(skills[0]['name'], 'Technical Writing')

    def test_resume_skills_scoped_to_authenticated_user(self):
        """resume_skills from another user's projects must not appear"""
        self.client.force_authenticate(user=self.user)

        other = User.objects.create_user(
            username='other2', email='other2@example.com', password='pass'
        )
        Project.objects.create(
            user=self.user, name='Mine', classification_type='writing',
            resume_skills=['Technical Writing']
        )
        Project.objects.create(
            user=other, name='Theirs', classification_type='writing',
            resume_skills=['Copywriting']
        )

        response = self.client.get(self.url)
        skill_names = [s['name'] for s in response.json()['resume_skills']]

        self.assertIn('Technical Writing', skill_names)
        self.assertNotIn('Copywriting', skill_names)
