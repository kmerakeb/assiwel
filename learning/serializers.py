from rest_framework import serializers
from .models import LearningSession, SessionItem, UserProgress, ItemMastery
from core.serializers import UserSerializer, LearningPathSerializer


class LearningSessionSerializer(serializers.ModelSerializer):
    class Meta:
        model = LearningSession
        fields = '__all__'


class SessionItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = SessionItem
        fields = '__all__'


class UserProgressSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProgress
        fields = '__all__'


class ItemMasterySerializer(serializers.ModelSerializer):
    class Meta:
        model = ItemMastery
        fields = '__all__'