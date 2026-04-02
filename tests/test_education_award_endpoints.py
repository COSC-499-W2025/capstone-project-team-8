from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from app.models import User, Education, Award

class EducationAwardEndpointsTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser', 
            email='test@example.com', 
            password='testpassword'
        )
        self.other_user = User.objects.create_user(
            username='otheruser', 
            email='other@example.com', 
            password='testpassword'
        )
        # Login standard user
        self.client.force_authenticate(user=self.user)
        
        # Education data
        self.edu_data = {
            "institution": "University of British Columbia",
            "degree": "B.Sc.",
            "major": "Computer Science",
            "start_date": "2020-09-01",
            "end_date": "2024-05-01",
            "currently_studying": False,
            "description": "Graduated with Honors."
        }
        
        # Award data
        self.award_data = {
            "title": "Dean's List",
            "issuer": "UBC",
            "date_received": "2023-05-01",
            "description": "Top 10% of class."
        }
        
        self.education_url = '/api/education/'
        self.award_url = '/api/awards/'

    def test_create_education(self):
        response = self.client.post(self.education_url, self.edu_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Education.objects.count(), 1)
        self.assertEqual(Education.objects.get().institution, 'University of British Columbia')

    def test_get_education_list(self):
        Education.objects.create(user=self.user, **self.edu_data)
        response = self.client.get(self.education_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['institution'], self.edu_data['institution'])
        
    def test_get_education_list_isolated(self):
        Education.objects.create(user=self.other_user, **self.edu_data)
        response = self.client.get(self.education_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 0)

    def test_create_award(self):
        response = self.client.post(self.award_url, self.award_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Award.objects.count(), 1)
        self.assertEqual(Award.objects.get().title, "Dean's List")

    def test_get_award_list(self):
        Award.objects.create(user=self.user, **self.award_data)
        response = self.client.get(self.award_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['title'], self.award_data['title'])
