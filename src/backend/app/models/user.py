from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.utils import timezone

class UserManager(BaseUserManager):
	"""Custom manager for User model"""
	def create_user(self, username, email, password=None, **extra_fields):
		if not username:
			raise ValueError('Username is required')
		if not email:
			raise ValueError('Email is required')
		email = self.normalize_email(email)
		user = self.model(username=username, email=email, **extra_fields)
		user.set_password(password)
		user.save(using=self._db)
		return user
	def create_superuser(self, username, email, password=None, **extra_fields):
		extra_fields.setdefault('is_staff', True)
		extra_fields.setdefault('is_superuser', True)
		extra_fields.setdefault('is_active', True)
		if extra_fields.get('is_staff') is not True:
			raise ValueError('Superuser must have is_staff=True')
		if extra_fields.get('is_superuser') is not True:
			raise ValueError('Superuser must have is_superuser=True')
		return self.create_user(username, email, password, **extra_fields)

class User(AbstractBaseUser, PermissionsMixin):
	username = models.CharField(max_length=150, unique=True, db_index=True)
	email = models.EmailField(max_length=255, unique=True)
	first_name = models.CharField(max_length=150, blank=True)
	last_name = models.CharField(max_length=150, blank=True)
	bio = models.TextField(max_length=500, blank=True)
	github_username = models.CharField(max_length=100, blank=True, db_index=True)
	github_email = models.EmailField(max_length=255, blank=True)
	linkedin_url = models.URLField(max_length=255, blank=True)
	portfolio_url = models.URLField(max_length=255, blank=True)
	twitter_username = models.CharField(max_length=100, blank=True)
	profile_image = models.ImageField(upload_to='profile_images/', null=True, blank=True)
	university = models.CharField(max_length=255, blank=True)
	degree_major = models.CharField(max_length=255, blank=True)
	education_city = models.CharField(max_length=100, blank=True)
	education_state = models.CharField(max_length=100, blank=True)
	expected_graduation = models.DateField(null=True, blank=True)
	is_active = models.BooleanField(default=True)
	is_staff = models.BooleanField(default=False)
	is_superuser = models.BooleanField(default=False)
	date_joined = models.DateTimeField(auto_now_add=True)
	last_login = models.DateTimeField(null=True, blank=True)
	profile_updated_at = models.DateTimeField(auto_now=True)
	objects = UserManager()
	USERNAME_FIELD = 'username'
	REQUIRED_FIELDS = ['email']
	class Meta:
		db_table = 'users'
		verbose_name = 'User'
		verbose_name_plural = 'Users'
	def __str__(self):
		return self.username
	def get_full_name(self):
		if self.first_name and self.last_name:
			return f"{self.first_name} {self.last_name}"
		return self.username
	def get_short_name(self):
		return self.first_name if self.first_name else self.username
	@property
	def display_name(self):
		return self.get_full_name()
	@property
	def profile_image_url(self):
		if self.profile_image:
			return self.profile_image.url
		return ''
"""User model and manager."""
