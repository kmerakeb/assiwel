from django.db import models
from uuid import uuid4
from core.models import User, Organization


class Notification(models.Model):
    """
    Notification system for the platform.
    """
    NOTIFICATION_TYPES = [
        ('info', 'Information'),
        ('warning', 'Warning'),
        ('error', 'Error'),
        ('achievement', 'Achievement'),
        ('reminder', 'Reminder'),
        ('system', 'System'),
        ('progress', 'Progress Update'),
    ]
    
    CHANNELS = [
        ('in_app', 'In-App'),
        ('email', 'Email'),
        ('push', 'Push Notification'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    message = models.TextField()
    notification_type = models.CharField(max_length=20, choices=NOTIFICATION_TYPES)
    channels = models.JSONField(default=list, help_text="List of channels to send notification to")
    is_read = models.BooleanField(default=False)
    read_at = models.DateTimeField(null=True, blank=True)
    scheduled_at = models.DateTimeField(null=True, blank=True)
    sent_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'notifications'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Notification: {self.title} - {self.user.get_full_name()}"


class UserLearningPreferences(models.Model):
    """
    User preferences for learning experience.
    """
    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='learning_preferences')
    preferred_difficulty = models.IntegerField(default=2, help_text="1-5 scale")
    daily_goal_xp = models.PositiveIntegerField(default=50)
    daily_goal_minutes = models.PositiveIntegerField(default=20)
    reminder_time = models.TimeField(null=True, blank=True)
    enable_daily_reminders = models.BooleanField(default=True)
    enable_weekly_summary = models.BooleanField(default=True)
    preferred_learning_times = models.JSONField(default=list, help_text="List of preferred learning time slots")
    learning_mode = models.CharField(
        max_length=20, 
        choices=[('adaptive', 'Adaptive'), ('structured', 'Structured'), ('free', 'Free')], 
        default='adaptive'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'user_learning_preferences'
    
    def __str__(self):
        return f"Preferences: {self.user.get_full_name()}"


class UserLearningHistory(models.Model):
    """
    Historical data for user learning patterns.
    """
    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='learning_history')
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE)
    date = models.DateField()
    session_count = models.PositiveIntegerField(default=0)
    minutes_spent = models.PositiveIntegerField(default=0)
    items_completed = models.PositiveIntegerField(default=0)
    xp_earned = models.PositiveIntegerField(default=0)
    accuracy_rate = models.FloatField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'user_learning_history'
        unique_together = ['user', 'date']
        ordering = ['-date']
    
    def __str__(self):
        return f"History: {self.user.get_full_name()} - {self.date}"
