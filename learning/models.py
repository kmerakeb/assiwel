from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from uuid import uuid4
from core.models import User, Organization, LearningItem


class LearningSession(models.Model):
    """
    Represents a learning session for a user.
    """
    SESSION_STATES = [
        ('not_started', 'Not Started'),
        ('in_progress', 'In Progress'),
        ('paused', 'Paused'),
        ('completed', 'Completed'),
        ('abandoned', 'Abandoned'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='learning_sessions')
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    state = models.CharField(max_length=20, choices=SESSION_STATES, default='not_started')
    started_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    estimated_duration = models.IntegerField(help_text="Estimated duration in minutes")
    actual_duration = models.IntegerField(help_text="Actual duration in minutes", null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'learning_sessions'
    
    def __str__(self):
        return f"{self.title} - {self.user.get_full_name()}"


class SessionItem(models.Model):
    """
    Individual item within a learning session.
    """
    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    session = models.ForeignKey(LearningSession, on_delete=models.CASCADE, related_name='session_items')
    learning_item = models.ForeignKey(LearningItem, on_delete=models.CASCADE)
    order = models.PositiveIntegerField()
    started_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    is_completed = models.BooleanField(default=False)
    score = models.FloatField(
        validators=[MinValueValidator(0.0), MaxValueValidator(1.0)], 
        null=True, 
        blank=True
    )
    attempts = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'session_items'
        ordering = ['order']
    
    def __str__(self):
        return f"{self.learning_item.title} in {self.session.title}"


class UserProgress(models.Model):
    """
    Tracks user progress for learning items.
    """
    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='progress_records')
    learning_item = models.ForeignKey(LearningItem, on_delete=models.CASCADE, related_name='progress_records')
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE)
    is_completed = models.BooleanField(default=False)
    completion_percentage = models.FloatField(
        validators=[MinValueValidator(0.0), MaxValueValidator(1.0)], 
        default=0.0
    )
    current_score = models.FloatField(
        validators=[MinValueValidator(0.0), MaxValueValidator(1.0)], 
        null=True, 
        blank=True
    )
    attempts = models.PositiveIntegerField(default=0)
    first_attempt_at = models.DateTimeField(null=True, blank=True)
    last_attempt_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'user_progress'
        unique_together = ['user', 'learning_item']
    
    def __str__(self):
        return f"Progress: {self.user.get_full_name()} - {self.learning_item.title}"


class ItemMastery(models.Model):
    """
    Tracks mastery level of learning items for users.
    """
    MASTERY_LEVELS = [
        (1, 'Beginner'),
        (2, 'Developing'),
        (3, 'Proficient'),
        (4, 'Advanced'),
        (5, 'Master'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='mastery_records')
    learning_item = models.ForeignKey(LearningItem, on_delete=models.CASCADE, related_name='mastery_records')
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE)
    mastery_level = models.IntegerField(choices=MASTERY_LEVELS, default=1)
    mastery_score = models.FloatField(
        validators=[MinValueValidator(0.0), MaxValueValidator(1.0)], 
        default=0.0
    )
    next_review_date = models.DateTimeField(null=True, blank=True)
    last_reviewed_at = models.DateTimeField(null=True, blank=True)
    review_count = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'item_mastery'
        unique_together = ['user', 'learning_item']
    
    def __str__(self):
        return f"Mastery: {self.user.get_full_name()} - {self.learning_item.title} (Level {self.mastery_level})"
