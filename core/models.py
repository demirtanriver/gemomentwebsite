# core/models.py

from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.utils import timezone
from django.core.validators import FileExtensionValidator
from storages.backends.s3boto3 import S3Boto3Storage
from django.conf import settings
import uuid 
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin 

# Custom Manager for Organisers
class OrganiserManager(BaseUserManager):
    def create_user(self, email, first_name, last_name, password=None, **extra_fields):
        if not email:
            raise ValueError('The Email field must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, first_name=first_name, last_name=last_name, **extra_fields)
        user.set_password(password) # set_password handles hashing
        user.save(using=self._db)
        return user

    def create_superuser(self, email, first_name, last_name, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True) 

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self.create_user(email, first_name, last_name, password, **extra_fields)


# Your Organisers Model, now a Custom User Model
class Organisers(AbstractBaseUser, PermissionsMixin):
    # Personal Information
    first_name = models.CharField(max_length=200, null=False)
    last_name = models.CharField(max_length=200, null=False)
    email = models.EmailField(max_length=255, unique=True, null=False)
    
    # password_hash field is implicitly provided by AbstractBaseUser as 'password'

    # Optional Contact Information
    address = models.TextField(null=True, blank=True)
    phone_number = models.CharField(max_length=50, null=True, blank=True)

    # Required fields for AbstractBaseUser and PermissionsMixin
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False) # Allows access to Django Admin
    date_joined = models.DateTimeField(default=timezone.now) # Required by AbstractBaseUser

    # Link to the custom manager
    objects = OrganiserManager()

    # Define the field used as the unique identifier for login
    USERNAME_FIELD = 'email'
    
    # Fields that will be prompted when creating a user via `createsuperuser`
    REQUIRED_FIELDS = ['first_name', 'last_name']
    
    # Fix for reverse accessor clashes.
    # We add a unique related_name for the many-to-many fields
    groups = models.ManyToManyField(
        'auth.Group',
        related_name='organiser_users',  # Custom related name
        blank=True,
        help_text=('The groups this user belongs to. A user will get all permissions '
                   'granted to each of their groups.'),
        verbose_name='groups',
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        related_name='organiser_users',  # Custom related name
        blank=True,
        help_text='Specific permissions for this user.',
        verbose_name='user permissions',
    )


    class Meta:
        verbose_name_plural = "Organisers" # Fixes pluralization in Django admin

    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.email})"

    # Methods required by PermissionsMixin
    def get_full_name(self):
        return f"{self.first_name} {self.last_name}"

    def get_short_name(self):
        return self.first_name

class Stories(models.Model):
    organiser = models.ForeignKey(Organisers, on_delete=models.CASCADE, related_name='stories')
    title = models.CharField(max_length=255)
    main_message = models.TextField()
    reveal_date = models.DateField()
    qr_code_url = models.URLField(max_length=500, blank=True, null=True) 
    topper_identifier = models.CharField(
        max_length=100, 
        unique=True, 
        blank=False, 
        null=False,  
        help_text="Unique code printed on the physical cake topper's QR code."
    )
    max_senders = models.PositiveIntegerField(
        default=6, 
        help_text="Maximum number of senders allowed to contribute to this story."
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = "Stories" 

    def __str__(self):
        return self.title

class Senders(models.Model):
    email = models.EmailField(max_length=255, unique=True, null=False)
    name = models.CharField(max_length=255, null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.email

    class Meta:
        verbose_name_plural = "Senders" 

class StorySenders(models.Model):
    story = models.ForeignKey(
        'Stories',
        on_delete=models.CASCADE, 
        related_name='story_links' 
    )
    sender = models.ForeignKey(
        'Senders',
        on_delete=models.CASCADE, 
        related_name='story_links' 
    )

    INVITATION_STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('sent', 'Sent'),
        ('accepted', 'Accepted'),
        ('uploaded', 'Uploaded Media'),
        ('revoked', 'Revoked'),
    ]
    invitation_status = models.CharField(
        max_length=50,
        choices=INVITATION_STATUS_CHOICES,
        default='pending',
        null=False
    )
    invitation_token = models.CharField(max_length=255, unique=True, null=True, blank=True)
    token_expires_at = models.DateTimeField(null=True, blank=True)
    invited_at = models.DateTimeField(auto_now_add=True)
    last_reminded_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        unique_together = ('story', 'sender')
        verbose_name_plural = "Story Senders" 

    def __str__(self):
        return f"{self.story.title} - {self.sender.email} ({self.invitation_status})"

# Base Contribution Model (Abstract)
class BaseContribution(models.Model):
    story_sender = models.ForeignKey(StorySenders, on_delete=models.CASCADE)
    caption = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('ignored', 'Ignored'), 
    ]
    status = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES,
        default='pending'
    )

    class Meta:
        abstract = True
        ordering = ['created_at'] 

CONTRIBUTION_STATUS_CHOICES = [
    ('pending', 'Pending Review'),
    ('approved', 'Approved'),
    ('ignored', 'Ignored'),
]

# Define your S3 storage instance
S3_MEDIA_STORAGE = S3Boto3Storage()

class ImageContribution(models.Model):
    story_sender = models.ForeignKey(StorySenders, on_delete=models.CASCADE, related_name='image_contributions')
    image = models.ImageField(upload_to='contributions/images/', storage=S3_MEDIA_STORAGE)
    caption = models.CharField(max_length=500, blank=True, null=True)
    status = models.CharField(max_length=10, choices=CONTRIBUTION_STATUS_CHOICES, default='pending') 
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Image by {self.story_sender.sender.email} for {self.story_sender.story.title}"

class VideoContribution(models.Model):
    story_sender = models.ForeignKey(StorySenders, on_delete=models.CASCADE, related_name='video_contributions')
    video = models.FileField(upload_to='contributions/videos/', blank=True, null=True, storage=S3_MEDIA_STORAGE)
    youtube_video_id = models.CharField(max_length=20, blank=True, null=True)
    caption = models.CharField(max_length=500, blank=True, null=True)
    status = models.CharField(max_length=10, choices=CONTRIBUTION_STATUS_CHOICES, default='pending') 
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Video by {self.story_sender.sender.email} for {self.story_sender.story.title}"

class TextContribution(models.Model):
    story_sender = models.ForeignKey(StorySenders, on_delete=models.CASCADE, related_name='text_contributions')
    content = models.TextField()
    status = models.CharField(max_length=10, choices=CONTRIBUTION_STATUS_CHOICES, default='pending') 
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Text by {self.story_sender.sender.email} for {self.story_sender.story.title}"
