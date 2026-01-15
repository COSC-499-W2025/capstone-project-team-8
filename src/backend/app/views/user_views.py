from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.contrib.auth import authenticate
import re
import logging

logger = logging.getLogger(__name__)

from app.models import User


@method_decorator(csrf_exempt, name="dispatch")
class UserMeView(APIView):
	"""GET/PUT current authenticated user's profile."""

	permission_classes = [IsAuthenticated]

	def _build_absolute_url(self, request, relative_url):
		"""Build absolute URL from relative path"""
		if not relative_url:
			return ''
		if relative_url.startswith('http'):
			return relative_url
		return request.build_absolute_uri(relative_url)

	def _user_to_dict(self, user, request=None, include_email=False):
		profile_image_url = user.profile_image_url
		if profile_image_url and request:
			profile_image_url = self._build_absolute_url(request, profile_image_url)
		
		out = {
			'username': user.username,
			'first_name': user.first_name,
			'last_name': user.last_name,
			'bio': user.bio,
			'github_username': user.github_username,
			'linkedin_url': user.linkedin_url,
			'portfolio_url': user.portfolio_url,
			'twitter_username': user.twitter_username,
			'profile_image_url': profile_image_url,
			'university': user.university,
			'degree_major': user.degree_major,
			'education_city': user.education_city,
			'education_state': user.education_state,
			'expected_graduation': user.expected_graduation.isoformat() if user.expected_graduation else None,
			'date_joined': user.date_joined.isoformat() if user.date_joined else None,
		}
		if include_email:
			out['email'] = user.email
		return out

	def get(self, request):
		user = request.user
		return JsonResponse({'user': self._user_to_dict(user, request=request, include_email=True)})

	def put(self, request):
		user = request.user
		try:
			if hasattr(request, 'data'):
				data = request.data
			else:
				import json
				data = json.loads(request.body) if request.body else {}
		except Exception as e:
			logger.error("Error parsing request data: %s", str(e))
			return JsonResponse({'detail': 'Invalid JSON in request body'}, status=400)

		if isinstance(data, dict) and 'user' in data and isinstance(data['user'], dict):
			data = data['user']
			
		allowed = [
			'first_name', 'last_name', 'bio', 'github_username',
			'linkedin_url', 'portfolio_url', 'twitter_username', 'profile_image_url',
			'university', 'degree_major', 'education_city', 'education_state', 'expected_graduation'
		]

		changed = False
		for k in allowed:
			if k in data:
				val = data.get(k)
				
				# Handle date field specially
				if k == 'expected_graduation':
					if val is None:
						setattr(user, k, None)
						changed = True
					elif isinstance(val, str):
						# Parse date string (expects YYYY-MM-DD format)
						try:
							from datetime import datetime
							parsed_date = datetime.strptime(val, '%Y-%m-%d').date()
							setattr(user, k, parsed_date)
							changed = True
						except ValueError:
							logger.warning("Invalid date format for expected_graduation: %s", val)
				# Basic type safety for other fields: require strings or None
				elif val is None or isinstance(val, str):
					logger.debug("Setting attribute %s => %r on user %s", k, val, user)
					setattr(user, k, val)
					changed = True

		# Ignore any attempt to change email (if present in payload)
		if 'email' in data:
			# Optionally you could return an error instead of silently ignoring.
			pass

		if changed:
			user.save()

		return JsonResponse({'user': self._user_to_dict(user, request=request, include_email=True)})



@method_decorator(csrf_exempt, name="dispatch")
class PublicUserView(APIView):
	"""GET public profile by username."""

	permission_classes = [AllowAny]

	def _build_absolute_url(self, request, relative_url):
		"""Build absolute URL from relative path"""
		if not relative_url:
			return ''
		if relative_url.startswith('http'):
			return relative_url
		return request.build_absolute_uri(relative_url)

	def _user_to_dict(self, user, request=None):
		profile_image_url = user.profile_image_url
		if profile_image_url and request:
			profile_image_url = self._build_absolute_url(request, profile_image_url)
		
		return {
			'username': user.username,
			'bio': user.bio,
			'profile_image_url': profile_image_url,
			'date_joined': user.date_joined.isoformat() if user.date_joined else None,
		}

	def get(self, request, username):
		user = get_object_or_404(User, username=username)
		return JsonResponse({'user': self._user_to_dict(user, request=request)})


@method_decorator(csrf_exempt, name="dispatch")
class PasswordChangeView(APIView):
	"""PUT endpoint to change user password."""

	permission_classes = [IsAuthenticated]

	def put(self, request):
		user = request.user
		try:
			data = request.data if hasattr(request, 'data') else {}
		except Exception:
			data = {}

		# Get password fields
		current_password = data.get('current_password', '')
		new_password = data.get('new_password', '')

		# Validate current password
		if not authenticate(username=user.username, password=current_password):
			return JsonResponse(
				{'detail': 'Current password is incorrect'},
				status=400
			)

		# Validate new password
		if not new_password:
			return JsonResponse(
				{'detail': 'New password is required'},
				status=400
			)

		if len(new_password) < 8:
			return JsonResponse(
				{'detail': 'Password must be at least 8 characters long'},
				status=400
			)

		# Update password
		user.set_password(new_password)
		user.save()

		return JsonResponse({
			'detail': 'Password updated successfully',
			'user': {
				'username': user.username,
				'email': user.email,
			}
		})


@method_decorator(csrf_exempt, name="dispatch")
class ProfileImageUploadView(APIView):
	"""POST endpoint to upload user profile image."""

	permission_classes = [IsAuthenticated]

	def post(self, request):
		user = request.user
		
		if 'profile_image' not in request.FILES:
			return JsonResponse({'detail': 'No image file provided'}, status=400)
		
		image_file = request.FILES['profile_image']
		
		# Validate file is an image
		if not image_file.content_type.startswith('image/'):
			return JsonResponse({'detail': 'File must be an image'}, status=400)
		
		# Optional: Check file size (e.g., max 5MB)
		if image_file.size > 5 * 1024 * 1024:
			return JsonResponse({'detail': 'Image must be smaller than 5MB'}, status=400)
		
		# Delete old image if exists
		if user.profile_image:
			user.profile_image.delete()
		
		# Save new image
		user.profile_image = image_file
		user.save()
		
		# Build absolute URL for the image
		profile_image_url = user.profile_image_url
		if profile_image_url:
			profile_image_url = request.build_absolute_uri(profile_image_url)
		
		return JsonResponse({
			'detail': 'Profile image uploaded successfully',
			'user': {
				'username': user.username,
				'profile_image_url': profile_image_url,
			}
		})






