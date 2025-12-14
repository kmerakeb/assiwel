from django.db import models
from uuid import uuid4
from core.models import User, Organization


class AIModel(models.Model):
    """
    AI model configuration and metadata.
    """
    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    name = models.CharField(max_length=255, unique=True)
    version = models.CharField(max_length=50)
    description = models.TextField(blank=True)
    model_type = models.CharField(max_length=50, help_text="e.g., 'language', 'speech', 'vision'")
    provider = models.CharField(max_length=50, default='ollama')
    provider_model_name = models.CharField(max_length=255)
    is_active = models.BooleanField(default=True)
    max_tokens = models.PositiveIntegerField(default=2048)
    temperature = models.FloatField(default=0.7)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'ai_models'
    
    def __str__(self):
        return f"{self.name} v{self.version}"


class AIPromptTemplate(models.Model):
    """
    Prompt templates for different AI use cases.
    """
    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    template = models.TextField(help_text="Template with placeholders like {input}, {context}, etc.")
    model = models.ForeignKey(AIModel, on_delete=models.CASCADE, related_name='prompt_templates')
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE, null=True, blank=True)
    variables = models.JSONField(default=list, help_text="List of required template variables")
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'ai_prompt_templates'
    
    def __str__(self):
        return self.name


class AIInteraction(models.Model):
    """
    Log of AI interactions for analysis and safety.
    """
    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='ai_interactions', null=True, blank=True)
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE)
    prompt_template = models.ForeignKey(AIPromptTemplate, on_delete=models.SET_NULL, null=True, blank=True)
    input_text = models.TextField()
    output_text = models.TextField()
    model_used = models.ForeignKey(AIModel, on_delete=models.SET_NULL, null=True, blank=True)
    input_tokens = models.PositiveIntegerField()
    output_tokens = models.PositiveIntegerField()
    processing_time = models.FloatField(help_text="Time taken in seconds")
    safety_score = models.FloatField(null=True, blank=True, help_text="Safety/risk score")
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'ai_interactions'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"AI Interaction: {self.user.get_full_name() if self.user else 'Anonymous'}"


class AISafetyFilter(models.Model):
    """
    Safety filters and content moderation rules.
    """
    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    filter_type = models.CharField(max_length=50, choices=[
        ('content_moderation', 'Content Moderation'),
        ('toxicity_detection', 'Toxicity Detection'),
        ('bias_detection', 'Bias Detection'),
        ('privacy_protection', 'Privacy Protection'),
    ])
    rules = models.JSONField(help_text="Filter rules in JSON format")
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'ai_safety_filters'
    
    def __str__(self):
        return self.name


class AICache(models.Model):
    """
    Cache for AI responses to improve performance.
    """
    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    cache_key = models.CharField(max_length=255, unique=True)
    input_hash = models.CharField(max_length=255, unique=True)
    response = models.TextField()
    model = models.ForeignKey(AIModel, on_delete=models.CASCADE)
    expires_at = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'ai_cache'
    
    def __str__(self):
        return f"Cache: {self.cache_key[:50]}..."


class AIUsageMetering(models.Model):
    """
    Track AI usage for billing and optimization.
    """
    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='ai_usage', null=True, blank=True)
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE)
    model = models.ForeignKey(AIModel, on_delete=models.CASCADE)
    input_tokens = models.PositiveIntegerField(default=0)
    output_tokens = models.PositiveIntegerField(default=0)
    requests_count = models.PositiveIntegerField(default=0)
    processing_time_total = models.FloatField(default=0.0)
    date = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'ai_usage_metering'
        unique_together = ['user', 'model', 'date']
        ordering = ['-date', '-created_at']
    
    def __str__(self):
        return f"AI Usage: {self.user.get_full_name() if self.user else 'System'} - {self.model.name}"
