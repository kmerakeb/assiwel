from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from uuid import uuid4
from core.models import User, Organization, Category, SubCategory, Topic


class ContentAuthoring(models.Model):
    """
    Content authoring workflow (draft, review, publish, versioning).
    """
    CONTENT_STATES = [
        ('draft', 'Draft'),
        ('review', 'Under Review'),
        ('revisions', 'Requiring Revisions'),
        ('approved', 'Approved'),
        ('published', 'Published'),
        ('archived', 'Archived'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    title = models.CharField(max_length=255)
    content = models.TextField()
    state = models.CharField(max_length=20, choices=CONTENT_STATES, default='draft')
    category = models.ForeignKey(Category, on_delete=models.CASCADE, null=True, blank=True)
    subcategory = models.ForeignKey(SubCategory, on_delete=models.CASCADE, null=True, blank=True)
    topic = models.ForeignKey(Topic, on_delete=models.CASCADE, null=True, blank=True)
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='created_content')
    reviewed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='reviewed_content', blank=True)
    approved_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='approved_content', blank=True)
    version = models.CharField(max_length=20, default='1.0')
    parent_content = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='versions')
    published_at = models.DateTimeField(null=True, blank=True)
    reviewed_at = models.DateTimeField(null=True, blank=True)
    approved_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'content_authoring'
    
    def __str__(self):
        return f"{self.title} - {self.state}"


class LearningItemTag(models.Model):
    """
    Tags for learning items to improve discoverability.
    """
    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'learning_item_tags'
    
    def __str__(self):
        return self.name


class LearningItemResource(models.Model):
    """
    Additional resources for learning items (files, links, etc.).
    """
    RESOURCE_TYPES = [
        ('document', 'Document'),
        ('image', 'Image'),
        ('audio', 'Audio'),
        ('video', 'Video'),
        ('link', 'External Link'),
        ('interactive', 'Interactive'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    name = models.CharField(max_length=255)
    resource_type = models.CharField(max_length=20, choices=RESOURCE_TYPES)
    file = models.FileField(upload_to='learning_resources/', blank=True, null=True)
    external_url = models.URLField(blank=True, null=True)
    description = models.TextField(blank=True)
    learning_item = models.ForeignKey('core.LearningItem', on_delete=models.CASCADE, related_name='resources')
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'learning_item_resources'
    
    def __str__(self):
        return f"{self.name} - {self.resource_type}"


class ContentFeedback(models.Model):
    """
    Feedback on content quality and effectiveness.
    """
    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='content_feedback')
    learning_item = models.ForeignKey('core.LearningItem', on_delete=models.CASCADE, related_name='feedback')
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE)
    rating = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)], 
        help_text="1-5 rating"
    )
    comment = models.TextField(blank=True)
    is_anonymous = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'content_feedback'
        unique_together = ['user', 'learning_item']
    
    def __str__(self):
        return f"Feedback: {self.user.get_full_name()} on {self.learning_item.title}"


class ContentUsageStats(models.Model):
    """
    Statistics on content usage and effectiveness.
    """
    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    learning_item = models.ForeignKey('core.LearningItem', on_delete=models.CASCADE, related_name='usage_stats')
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE)
    total_attempts = models.PositiveIntegerField(default=0)
    total_completions = models.PositiveIntegerField(default=0)
    average_score = models.FloatField(default=0.0)
    completion_rate = models.FloatField(default=0.0)
    avg_time_spent = models.FloatField(default=0.0)  # in minutes
    last_accessed_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'content_usage_stats'
        unique_together = ['learning_item', 'organization']
    
    def __str__(self):
        return f"Stats: {self.learning_item.title}"
