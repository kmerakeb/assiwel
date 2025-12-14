from django.db import models
from uuid import uuid4
from core.models import User, Organization


class SpeechRecognitionResult(models.Model):
    """
    Results from speech recognition (ASR) processing.
    """
    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='speech_recognition_results')
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE)
    audio_file = models.FileField(upload_to='speech_audio/')
    transcript = models.TextField()
    confidence_score = models.FloatField(help_text="Confidence score between 0 and 1")
    processing_time = models.FloatField(help_text="Time taken in seconds")
    language = models.CharField(max_length=10, default='en')
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'speech_recognition_results'
    
    def __str__(self):
        return f"ASR Result: {self.user.get_full_name()} - {self.confidence_score:.2f}"


class PronunciationAssessment(models.Model):
    """
    Pronunciation scoring and assessment.
    """
    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='pronunciation_assessments')
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE)
    speech_result = models.OneToOneField(SpeechRecognitionResult, on_delete=models.CASCADE, related_name='pronunciation_assessment')
    reference_text = models.TextField()
    pronunciation_score = models.FloatField(help_text="Pronunciation score between 0 and 1")
    accuracy_score = models.FloatField(help_text="Accuracy score between 0 and 1")
    fluency_score = models.FloatField(help_text="Fluency score between 0 and 1")
    completeness_score = models.FloatField(help_text="Completeness score between 0 and 1")
    prosody_score = models.FloatField(help_text="Prosody score between 0 and 1", null=True, blank=True)
    detailed_feedback = models.JSONField(help_text="Detailed feedback in JSON format", null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'pronunciation_assessments'
    
    def __str__(self):
        return f"Pronunciation Assessment: {self.user.get_full_name()} - {self.pronunciation_score:.2f}"


class TextToSpeechRequest(models.Model):
    """
    TTS generation requests and results.
    """
    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='tts_requests', null=True, blank=True)
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE)
    text = models.TextField()
    language = models.CharField(max_length=10, default='en')
    voice_type = models.CharField(max_length=50, default='default')
    audio_file = models.FileField(upload_to='tts_audio/', null=True, blank=True)
    processing_time = models.FloatField(help_text="Time taken in seconds", null=True, blank=True)
    is_completed = models.BooleanField(default=False)
    error_message = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        db_table = 'text_to_speech_requests'
    
    def __str__(self):
        return f"TTS Request: {self.text[:50]}..."


class SpeechTrainingItem(models.Model):
    """
    Items for speech training and practice.
    """
    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    text = models.TextField()
    language = models.CharField(max_length=10, default='en')
    phonetic_transcription = models.TextField(blank=True, help_text="IPA or other phonetic transcription")
    audio_reference = models.FileField(upload_to='speech_training_audio/', null=True, blank=True)
    difficulty_level = models.IntegerField(default=1, help_text="1-5 difficulty scale")
    category = models.CharField(max_length=100, blank=True)
    subcategory = models.CharField(max_length=100, blank=True)
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'speech_training_items'
    
    def __str__(self):
        return f"Speech Training: {self.text[:50]}..."


class SpeechSession(models.Model):
    """
    Speech practice sessions.
    """
    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='speech_sessions')
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    started_at = models.DateTimeField(auto_now_add=True)
    ended_at = models.DateTimeField(null=True, blank=True)
    total_attempts = models.PositiveIntegerField(default=0)
    average_pronunciation_score = models.FloatField(null=True, blank=True)
    completed_items = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'speech_sessions'
    
    def __str__(self):
        return f"Speech Session: {self.user.get_full_name()} - {self.title}"


class SpeechSessionItem(models.Model):
    """
    Individual item within a speech session.
    """
    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    session = models.ForeignKey(SpeechSession, on_delete=models.CASCADE, related_name='session_items')
    training_item = models.ForeignKey(SpeechTrainingItem, on_delete=models.CASCADE)
    order = models.PositiveIntegerField()
    started_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    pronunciation_assessment = models.ForeignKey(PronunciationAssessment, on_delete=models.SET_NULL, null=True, blank=True)
    is_completed = models.BooleanField(default=False)
    attempts = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'speech_session_items'
        ordering = ['order']
    
    def __str__(self):
        return f"Session Item: {self.training_item.text[:30]}... in {self.session.title}"
