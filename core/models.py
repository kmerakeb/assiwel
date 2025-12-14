from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone
from django.core.validators import MinValueValidator, MaxValueValidator
from uuid import uuid4
import os


class Organization(models.Model):
    """
    Represents an organization in the multi-tenant system.
    """
    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    name = models.CharField(max_length=255, unique=True)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        db_table = 'organizations'
        verbose_name_plural = 'Organizations'
    
    def __str__(self):
        return self.name


class User(AbstractUser):
    """
    Custom User model with organization and role support.
    """
    USER_ROLES = [
        ('admin', 'Administrator'),
        ('instructor', 'Instructor'),
        ('learner', 'Learner'),
        ('content_manager', 'Content Manager'),
        ('observer', 'Observer'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE, related_name='users')
    role = models.CharField(max_length=20, choices=USER_ROLES, default='learner')
    email = models.EmailField(unique=True)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name', 'organization']
    
    class Meta:
        db_table = 'users'
        verbose_name_plural = 'Users'
    
    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.email})"


class Profile(models.Model):
    """
    Extended user profile information.
    """
    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    bio = models.TextField(blank=True)
    date_of_birth = models.DateField(null=True, blank=True)
    native_language = models.CharField(max_length=10, default='en')  # ISO language code
    timezone = models.CharField(max_length=50, default='UTC')
    preferred_locale = models.CharField(max_length=10, default='en')
    phone_number = models.CharField(max_length=20, blank=True)
    address = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'profiles'
    
    def __str__(self):
        return f"Profile for {self.user.get_full_name()}"


class Category(models.Model):
    """
    Learning category (e.g., grammar, vocabulary, pronunciation).
    """
    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE, related_name='categories')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        db_table = 'categories'
        verbose_name_plural = 'Categories'
        unique_together = ['name', 'organization']
    
    def __str__(self):
        return f"{self.name} ({self.organization.name})"


class SubCategory(models.Model):
    """
    Subcategory under a category.
    """
    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='subcategories')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        db_table = 'subcategories'
        verbose_name_plural = 'Subcategories'
        unique_together = ['name', 'category']
    
    def __str__(self):
        return f"{self.name} ({self.category.name})"


class Topic(models.Model):
    """
    Specific topic under a subcategory.
    """
    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    title = models.CharField(max_length=255)
    content = models.TextField()
    subcategory = models.ForeignKey(SubCategory, on_delete=models.CASCADE, related_name='topics')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        db_table = 'topics'
    
    def __str__(self):
        return self.title


class LearningPath(models.Model):
    """
    Personalized learning path for a user.
    """
    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='learning_paths')
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)
    is_completed = models.BooleanField(default=False)
    
    class Meta:
        db_table = 'learning_paths'
    
    def __str__(self):
        return f"{self.name} - {self.user.get_full_name()}"


class LearningItem(models.Model):
    """
    Abstract base for different types of learning items.
    """
    ITEM_TYPES = [
        ('vocabulary', 'Vocabulary'),
        ('listening', 'Listening'),
        ('speaking', 'Speaking'),
        ('multiple_choice', 'Multiple Choice'),
        ('reading', 'Reading'),
        ('writing', 'Writing'),
        ('grammar', 'Grammar'),
        ('conversation', 'Conversation'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    title = models.CharField(max_length=255)
    content = models.TextField()
    item_type = models.CharField(max_length=20, choices=ITEM_TYPES)
    difficulty_level = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)], 
        default=1
    )
    estimated_duration = models.IntegerField(help_text="Estimated duration in minutes")
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='created_learning_items')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)
    is_published = models.BooleanField(default=False)
    
    class Meta:
        db_table = 'learning_items'
        abstract = True


class VocabularyItem(LearningItem):
    """
    Vocabulary-specific learning item.
    """
    word = models.CharField(max_length=255)
    definition = models.TextField()
    pronunciation = models.CharField(max_length=255, blank=True)
    example_sentence = models.TextField()
    synonyms = models.TextField(blank=True)  # JSON string
    antonyms = models.TextField(blank=True)  # JSON string
    audio_file = models.FileField(upload_to='vocabulary_audio/', blank=True, null=True)
    
    class Meta:
        db_table = 'vocabulary_items'
    
    def save(self, *args, **kwargs):
        self.item_type = 'vocabulary'
        super().save(*args, **kwargs)


class ListeningItem(LearningItem):
    """
    Listening-specific learning item.
    """
    audio_file = models.FileField(upload_to='listening_audio/')
    transcript = models.TextField()
    questions = models.TextField()  # JSON string for questions
    
    class Meta:
        db_table = 'listening_items'
    
    def save(self, *args, **kwargs):
        self.item_type = 'listening'
        super().save(*args, **kwargs)


class SpeakingItem(LearningItem):
    """
    Speaking-specific learning item.
    """
    prompt = models.TextField()
    target_language = models.CharField(max_length=10, default='en')
    audio_reference = models.FileField(upload_to='speaking_audio/', blank=True, null=True)
    
    class Meta:
        db_table = 'speaking_items'
    
    def save(self, *args, **kwargs):
        self.item_type = 'speaking'
        super().save(*args, **kwargs)


class MultipleChoiceItem(LearningItem):
    """
    Multiple choice-specific learning item.
    """
    question = models.TextField()
    options = models.TextField()  # JSON string for options
    correct_answer = models.CharField(max_length=255)
    explanation = models.TextField(blank=True)
    
    class Meta:
        db_table = 'multiple_choice_items'
    
    def save(self, *args, **kwargs):
        self.item_type = 'multiple_choice'
        super().save(*args, **kwargs)


class AuditLog(models.Model):
    """
    Audit log for compliance and security.
    """
    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='audit_logs')
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE, null=True, related_name='audit_logs')
    action = models.CharField(max_length=255)
    resource_type = models.CharField(max_length=100)
    resource_id = models.UUIDField()
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)
    request_data = models.JSONField(blank=True, null=True)
    response_data = models.JSONField(blank=True, null=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    success = models.BooleanField(default=True)
    
    class Meta:
        db_table = 'audit_logs'
        verbose_name_plural = 'Audit Logs'
        ordering = ['-timestamp']
    
    def __str__(self):
        return f"{self.action} - {self.user} - {self.timestamp}"


class AnalyticsEvent(models.Model):
    """
    Analytics event for tracking learning effectiveness.
    """
    EVENT_TYPES = [
        ('session_start', 'Session Start'),
        ('session_complete', 'Session Complete'),
        ('item_start', 'Item Start'),
        ('item_complete', 'Item Complete'),
        ('ai_interaction', 'AI Interaction'),
        ('speech_attempt', 'Speech Attempt'),
        ('achievement_unlocked', 'Achievement Unlocked'),
        ('progress_update', 'Progress Update'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='analytics_events')
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE)
    event_type = models.CharField(max_length=30, choices=EVENT_TYPES)
    event_data = models.JSONField()  # Flexible data storage
    timestamp = models.DateTimeField(auto_now_add=True)
    session_id = models.UUIDField(null=True, blank=True)
    learning_item_id = models.UUIDField(null=True, blank=True)
    
    class Meta:
        db_table = 'analytics_events'
        ordering = ['-timestamp']
    
    def __str__(self):
        return f"{self.event_type} - {self.user.get_full_name()}"
