from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin


class UserManager(BaseUserManager):
    """Custom manager for User model"""
    
    def create_user(self, username, email, password=None, **extra_fields):
        """
        Create and return a regular user with username, email and password.
        This method is called by auth.py: User.objects.create_user()
        """
        if not username:
            raise ValueError('Username is required')
        if not email:
            raise ValueError('Email is required')
        
        # Normalize email (lowercase the domain part)
        email = self.normalize_email(email)
        
        # Create user instance
        user = self.model(username=username, email=email, **extra_fields)
        
        # Hash the password (never store plain text!)
        user.set_password(password)
        
        # Save to database
        user.save(using=self._db)
        return user
    
    def create_superuser(self, username, email, password=None, **extra_fields):
        """
        Create and return a superuser for Django admin.
        Used by: python manage.py createsuperuser
        """
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)
        
        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True')
        
        return self.create_user(username, email, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    """
    Custom User model for the capstone project.
    Uses username for authentication (to match existing auth.py implementation).
    """
    # Core fields required by auth.py
    username = models.CharField(max_length=150, unique=True, db_index=True)
    email = models.EmailField(max_length=255, unique=True)
    
    # Permission fields (required for admin and authentication)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    
    # Timestamps
    date_joined = models.DateTimeField(auto_now_add=True)
    last_login = models.DateTimeField(null=True, blank=True)
    
    # Attach the custom manager
    objects = UserManager()
    
    # Tell Django to use 'username' for authentication
    # This matches auth.py: authenticate(username=username, password=password)
    USERNAME_FIELD = 'username'
    
    # Required fields when creating superuser
    REQUIRED_FIELDS = ['email']
    
    class Meta:
        db_table = 'users'
        verbose_name = 'User'
        verbose_name_plural = 'Users'
    
    def __str__(self):
        """String representation - used in admin and logging"""
        return self.username
    
    def get_full_name(self):
        """Return username as full name"""
        return self.username
    
    def get_short_name(self):
        """Return username as short name"""
        return self.username