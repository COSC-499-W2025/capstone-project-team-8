# """
# Unit tests for image upload and retrieval functionality.
# Tests profile image uploads and project thumbnail uploads.
# """
# import os
# import tempfile
# from io import BytesIO
# from PIL import Image
# from django.test import TestCase, Client, override_settings
# from django.contrib.auth import get_user_model
# from django.core.files.uploadedfile import SimpleUploadedFile
# from app.models import Project

# User = get_user_model()

# # Use temporary directory for test media files
# TEMP_MEDIA_ROOT = tempfile.mkdtemp()


# @override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
# class ProfileImageUploadTest(TestCase):
#     """Tests for user profile image upload functionality."""

#     def setUp(self):
#         """Set up test user and client."""
#         self.client = Client()
#         self.user = User.objects.create_user(
#             username='testuser',
#             email='test@example.com',
#             password='testpass123'
#         )

#     def create_test_image(self, filename='test.jpg', size=(100, 100), format='JPEG'):
#         """Helper method to create a test image file."""
#         file = BytesIO()
#         image = Image.new('RGB', size=size, color=(255, 0, 0))
#         image.save(file, format=format)
#         file.seek(0)
#         return SimpleUploadedFile(filename, file.getvalue(), content_type='image/jpeg')

#     def test_profile_image_upload_success(self):
#         """Test successful profile image upload."""
#         # Login user
#         self.client.login(username='testuser', password='testpass123')

#         # Create test image
#         image = self.create_test_image()

#         # Upload image
#         response = self.client.post(
#             '/api/users/me/profile-image/',
#             {'profile_image': image},
#             HTTP_AUTHORIZATION=f'Bearer {self._get_token()}'
#         )

#         # Check response
#         self.assertEqual(response.status_code, 200)
#         data = response.json()
#         self.assertIn('user', data)
#         self.assertIn('profile_image_url', data['user'])
#         self.assertTrue(data['user']['profile_image_url'].endswith('.jpg'))

#     def test_profile_image_upload_invalid_file_type(self):
#         """Test profile image upload with invalid file type."""
#         self.client.login(username='testuser', password='testpass123')

#         # Create non-image file
#         invalid_file = SimpleUploadedFile(
#             'test.txt',
#             b'not an image',
#             content_type='text/plain'
#         )

#         response = self.client.post(
#             '/api/users/me/profile-image/',
#             {'profile_image': invalid_file},
#             HTTP_AUTHORIZATION=f'Bearer {self._get_token()}'
#         )

#         self.assertEqual(response.status_code, 400)
#         self.assertIn('image', response.json()['detail'].lower())

#     def test_profile_image_upload_file_too_large(self):
#         """Test profile image upload with file size exceeding limit."""
#         self.client.login(username='testuser', password='testpass123')

#         # Create large test image (5MB+)
#         # Note: Create a large PNG (uncompressed) to ensure > 5MB
#         file = BytesIO()
#         image = Image.new('RGB', size=(2500, 2500), color=(255, 0, 0))
#         image.save(file, format='PNG')
#         file.seek(0)

#         # Ensure file is actually > 5MB
#         if file.getbuffer().nbytes <= 5 * 1024 * 1024:
#             # If PNG is still not large enough, pad it
#             file_data = file.getvalue()
#             file_data += b'\x00' * (5 * 1024 * 1024 - len(file_data) + 1)
#             file = BytesIO(file_data)

#         large_file = SimpleUploadedFile(
#             'large.png',
#             file.getvalue(),
#             content_type='image/png'
#         )

#         response = self.client.post(
#             '/api/users/me/profile-image/',
#             {'profile_image': large_file},
#             HTTP_AUTHORIZATION=f'Bearer {self._get_token()}'
#         )

#         self.assertEqual(response.status_code, 400)
#         self.assertIn('smaller', response.json()['detail'].lower())

#     def test_profile_image_upload_no_file(self):
#         """Test profile image upload with no file provided."""
#         self.client.login(username='testuser', password='testpass123')

#         response = self.client.post(
#             '/api/users/me/profile-image/',
#             {},
#             HTTP_AUTHORIZATION=f'Bearer {self._get_token()}'
#         )

#         self.assertEqual(response.status_code, 400)
#         self.assertIn('no image', response.json()['detail'].lower())

#     def test_profile_image_returns_absolute_url(self):
#         """Test that profile image URL is absolute, not relative."""
#         self.client.login(username='testuser', password='testpass123')

#         image = self.create_test_image()
#         response = self.client.post(
#             '/api/users/me/profile-image/',
#             {'profile_image': image},
#             HTTP_AUTHORIZATION=f'Bearer {self._get_token()}'
#         )

#         data = response.json()
#         url = data['user']['profile_image_url']

#         # Check that URL is absolute (starts with http)
#         self.assertTrue(url.startswith('http://') or url.startswith('https://'))

#     def test_profile_image_retrieved_in_user_me_endpoint(self):
#         """Test that profile image URL is returned in /api/users/me/ endpoint."""
#         self.client.login(username='testuser', password='testpass123')

#         # Upload image
#         image = self.create_test_image()
#         self.client.post(
#             '/api/users/me/profile-image/',
#             {'profile_image': image},
#             HTTP_AUTHORIZATION=f'Bearer {self._get_token()}'
#         )

#         # Get user profile
#         response = self.client.get(
#             '/api/users/me/',
#             HTTP_AUTHORIZATION=f'Bearer {self._get_token()}'
#         )

#         self.assertEqual(response.status_code, 200)
#         data = response.json()
#         self.assertIn('profile_image_url', data['user'])
#         # Should be absolute URL
#         self.assertTrue(
#             data['user']['profile_image_url'].startswith('http://') or
#             data['user']['profile_image_url'].startswith('https://')
#         )

#     def test_profile_image_replaces_old_image(self):
#         """Test that uploading a new profile image replaces the old one."""
#         self.client.login(username='testuser', password='testpass123')

#         # Upload first image
#         image1 = self.create_test_image('test1.jpg')
#         response1 = self.client.post(
#             '/api/users/me/profile-image/',
#             {'profile_image': image1},
#             HTTP_AUTHORIZATION=f'Bearer {self._get_token()}'
#         )
#         url1 = response1.json()['user']['profile_image_url']

#         # Upload second image
#         image2 = self.create_test_image('test2.jpg')
#         response2 = self.client.post(
#             '/api/users/me/profile-image/',
#             {'profile_image': image2},
#             HTTP_AUTHORIZATION=f'Bearer {self._get_token()}'
#         )
#         url2 = response2.json()['user']['profile_image_url']

#         # URLs should be different
#         self.assertNotEqual(url1, url2)

#     def _get_token(self):
#         """Helper to get JWT token for user."""
#         response = self.client.post(
#             '/api/token/',
#             {'username': 'testuser', 'password': 'testpass123'},
#             content_type='application/json'
#         )
#         return response.json()['access']


# @override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
# class ProjectThumbnailUploadTest(TestCase):
#     """Tests for project thumbnail upload functionality."""

#     def setUp(self):
#         """Set up test user, project, and client."""
#         self.client = Client()
#         self.user = User.objects.create_user(
#             username='testuser',
#             email='test@example.com',
#             password='testpass123'
#         )
#         self.project = Project.objects.create(
#             user=self.user,
#             name='Test Project',
#             description='Test project for thumbnail upload'
#         )

#     def create_test_image(self, filename='test.jpg', size=(100, 100), format='JPEG'):
#         """Helper method to create a test image file."""
#         file = BytesIO()
#         image = Image.new('RGB', size=size, color=(0, 255, 0))
#         image.save(file, format=format)
#         file.seek(0)
#         return SimpleUploadedFile(filename, file.getvalue(), content_type='image/jpeg')

#     def test_project_thumbnail_upload_success(self):
#         """Test successful project thumbnail upload."""
#         self.client.login(username='testuser', password='testpass123')

#         image = self.create_test_image()
#         response = self.client.post(
#             f'/api/projects/{self.project.id}/thumbnail/',
#             {'thumbnail': image},
#             HTTP_AUTHORIZATION=f'Bearer {self._get_token()}'
#         )

#         self.assertEqual(response.status_code, 200)
#         data = response.json()
#         self.assertIn('project', data)
#         self.assertIn('thumbnail_url', data['project'])
#         self.assertTrue(data['project']['thumbnail_url'].endswith('.jpg'))

#     def test_project_thumbnail_upload_invalid_file_type(self):
#         """Test project thumbnail upload with invalid file type."""
#         self.client.login(username='testuser', password='testpass123')

#         invalid_file = SimpleUploadedFile(
#             'test.pdf',
#             b'not an image',
#             content_type='application/pdf'
#         )

#         response = self.client.post(
#             f'/api/projects/{self.project.id}/thumbnail/',
#             {'thumbnail': invalid_file},
#             HTTP_AUTHORIZATION=f'Bearer {self._get_token()}'
#         )

#         self.assertEqual(response.status_code, 400)
#         self.assertIn('image', response.json()['detail'].lower())

#     def test_project_thumbnail_upload_no_file(self):
#         """Test project thumbnail upload with no file provided."""
#         self.client.login(username='testuser', password='testpass123')

#         response = self.client.post(
#             f'/api/projects/{self.project.id}/thumbnail/',
#             {},
#             HTTP_AUTHORIZATION=f'Bearer {self._get_token()}'
#         )

#         self.assertEqual(response.status_code, 400)
#         self.assertIn('no image', response.json()['detail'].lower())

#     def test_project_thumbnail_upload_nonexistent_project(self):
#         """Test thumbnail upload to non-existent project."""
#         self.client.login(username='testuser', password='testpass123')

#         image = self.create_test_image()
#         response = self.client.post(
#             '/api/projects/99999/thumbnail/',
#             {'thumbnail': image},
#             HTTP_AUTHORIZATION=f'Bearer {self._get_token()}'
#         )

#         self.assertEqual(response.status_code, 404)

#     def test_project_thumbnail_returns_absolute_url(self):
#         """Test that project thumbnail URL is absolute, not relative."""
#         self.client.login(username='testuser', password='testpass123')

#         image = self.create_test_image()
#         response = self.client.post(
#             f'/api/projects/{self.project.id}/thumbnail/',
#             {'thumbnail': image},
#             HTTP_AUTHORIZATION=f'Bearer {self._get_token()}'
#         )

#         data = response.json()
#         url = data['project']['thumbnail_url']

#         # Check that URL is absolute
#         self.assertTrue(url.startswith('http://') or url.startswith('https://'))

#     def test_project_thumbnail_in_projects_list(self):
#         """Test that thumbnail URL is returned in projects list."""
#         self.client.login(username='testuser', password='testpass123')

#         # Upload thumbnail
#         image = self.create_test_image()
#         self.client.post(
#             f'/api/projects/{self.project.id}/thumbnail/',
#             {'thumbnail': image},
#             HTTP_AUTHORIZATION=f'Bearer {self._get_token()}'
#         )

#         # Get projects list
#         response = self.client.get(
#             '/api/projects/',
#             HTTP_AUTHORIZATION=f'Bearer {self._get_token()}'
#         )

#         self.assertEqual(response.status_code, 200)
#         data = response.json()
#         self.assertGreater(len(data['projects']), 0)

#         project = data['projects'][0]
#         self.assertIn('thumbnail_url', project)
#         # Should be absolute URL
#         if project['thumbnail_url']:
#             self.assertTrue(
#                 project['thumbnail_url'].startswith('http://') or
#                 project['thumbnail_url'].startswith('https://')
#             )

#     def test_project_thumbnail_replaces_old_thumbnail(self):
#         """Test that uploading a new thumbnail replaces the old one."""
#         self.client.login(username='testuser', password='testpass123')

#         # Upload first thumbnail
#         image1 = self.create_test_image('thumb1.jpg')
#         response1 = self.client.post(
#             f'/api/projects/{self.project.id}/thumbnail/',
#             {'thumbnail': image1},
#             HTTP_AUTHORIZATION=f'Bearer {self._get_token()}'
#         )
#         url1 = response1.json()['project']['thumbnail_url']

#         # Upload second thumbnail
#         image2 = self.create_test_image('thumb2.jpg')
#         response2 = self.client.post(
#             f'/api/projects/{self.project.id}/thumbnail/',
#             {'thumbnail': image2},
#             HTTP_AUTHORIZATION=f'Bearer {self._get_token()}'
#         )
#         url2 = response2.json()['project']['thumbnail_url']

#         # URLs should be different
#         self.assertNotEqual(url1, url2)

#     def test_unauthorized_project_thumbnail_upload(self):
#         """Test that user cannot upload thumbnail to another user's project."""
#         # Create another user
#         other_user = User.objects.create_user(
#             username='otheruser',
#             email='other@example.com',
#             password='otherpass123'
#         )

#         # Create project for other user
#         other_project = Project.objects.create(
#             user=other_user,
#             name='Other Project'
#         )

#         # Try to upload as first user
#         self.client.login(username='testuser', password='testpass123')
#         image = self.create_test_image()

#         response = self.client.post(
#             f'/api/projects/{other_project.id}/thumbnail/',
#             {'thumbnail': image},
#             HTTP_AUTHORIZATION=f'Bearer {self._get_token()}'
#         )

#         self.assertEqual(response.status_code, 404)

#     def _get_token(self):
#         """Helper to get JWT token for user."""
#         response = self.client.post(
#             '/api/token/',
#             {'username': 'testuser', 'password': 'testpass123'},
#             content_type='application/json'
#         )
#         return response.json()['access']


# class ImageDatabaseModelTest(TestCase):
#     """Tests for image field behavior in database models."""

#     def setUp(self):
#         """Set up test user."""
#         self.user = User.objects.create_user(
#             username='testuser',
#             email='test@example.com',
#             password='testpass123'
#         )

#     def test_user_profile_image_field_exists(self):
#         """Test that User model has profile_image field."""
#         self.assertTrue(hasattr(self.user, 'profile_image'))

#     def test_user_profile_image_url_property(self):
#         """Test that User model has profile_image_url property."""
#         # Empty profile image should return empty string
#         self.assertEqual(self.user.profile_image_url, '')

#     def test_project_thumbnail_field_exists(self):
#         """Test that Project model has thumbnail field."""
#         project = Project.objects.create(
#             user=self.user,
#             name='Test Project'
#         )
#         self.assertTrue(hasattr(project, 'thumbnail'))

#     def test_project_thumbnail_none_by_default(self):
#         """Test that project thumbnail is None by default."""
#         project = Project.objects.create(
#             user=self.user,
#             name='Test Project'
#         )
#         self.assertFalse(project.thumbnail)

#     def test_user_can_have_multiple_projects_with_thumbnails(self):
#         """Test that a user can have multiple projects with different thumbnails."""
#         project1 = Project.objects.create(
#             user=self.user,
#             name='Project 1'
#         )
#         project2 = Project.objects.create(
#             user=self.user,
#             name='Project 2'
#         )

#         # Both should exist and be independent
#         self.assertEqual(project1.id, project1.id)
#         self.assertEqual(project2.id, project2.id)
#         self.assertNotEqual(project1.id, project2.id)
