from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from uuid import uuid4
from core.models import User, Organization


class Streak(models.Model):
    """
    Tracks user streaks for consistent learning.
    """
    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='streaks')
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE)
    current_streak = models.PositiveIntegerField(default=0)
    longest_streak = models.PositiveIntegerField(default=0)
    last_activity_date = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'streaks'
    
    def __str__(self):
        return f"Streak: {self.user.get_full_name()} - Current: {self.current_streak}"


class XPTransaction(models.Model):
    """
    Tracks XP transactions for gamification.
    """
    XP_TYPES = [
        ('learning_completion', 'Learning Completion'),
        ('daily_login', 'Daily Login'),
        ('streak_bonus', 'Streak Bonus'),
        ('achievement', 'Achievement'),
        ('referral', 'Referral'),
        ('bonus', 'Bonus'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='xp_transactions')
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE)
    xp_type = models.CharField(max_length=30, choices=XP_TYPES)
    amount = models.PositiveIntegerField()
    description = models.TextField(blank=True)
    related_id = models.UUIDField(null=True, blank=True, help_text="Related object ID (e.g., learning item ID)")
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'xp_transactions'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"XP: {self.user.get_full_name()} - {self.amount} ({self.xp_type})"


class Badge(models.Model):
    """
    Badges that can be earned by users.
    """
    BADGE_CATEGORIES = [
        ('milestone', 'Milestone'),
        ('achievement', 'Achievement'),
        ('behavior', 'Behavior'),
        ('performance', 'Performance'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    name = models.CharField(max_length=255)
    description = models.TextField()
    category = models.CharField(max_length=20, choices=BADGE_CATEGORIES)
    icon = models.CharField(max_length=100, blank=True, help_text="Icon class or URL")
    xp_reward = models.PositiveIntegerField(default=0)
    required_xp = models.PositiveIntegerField(null=True, blank=True)
    required_streak = models.PositiveIntegerField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'badges'
    
    def __str__(self):
        return self.name


class Achievement(models.Model):
    """
    User achievements (earned badges).
    """
    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='achievements')
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE)
    badge = models.ForeignKey(Badge, on_delete=models.CASCADE)
    earned_at = models.DateTimeField(auto_now_add=True)
    xp_earned = models.PositiveIntegerField(default=0)
    is_verified = models.BooleanField(default=True)
    
    class Meta:
        db_table = 'achievements'
        unique_together = ['user', 'badge']
    
    def __str__(self):
        return f"Achievement: {self.user.get_full_name()} - {self.badge.name}"
