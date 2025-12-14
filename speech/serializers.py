from rest_framework import serializers
from .models import SpeechRecognitionResult, PronunciationAssessment, TextToSpeechRequest, SpeechTrainingItem, SpeechSession, SpeechSessionItem


class SpeechRecognitionResultSerializer(serializers.ModelSerializer):
    class Meta:
        model = SpeechRecognitionResult
        fields = '__all__'


class PronunciationAssessmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = PronunciationAssessment
        fields = '__all__'


class TextToSpeechRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = TextToSpeechRequest
        fields = '__all__'


class SpeechTrainingItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = SpeechTrainingItem
        fields = '__all__'


class SpeechSessionSerializer(serializers.ModelSerializer):
    class Meta:
        model = SpeechSession
        fields = '__all__'


class SpeechSessionItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = SpeechSessionItem
        fields = '__all__'