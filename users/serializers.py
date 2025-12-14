from rest_framework import serializers
from .models import Notification, UserLearningPreferences, UserLearningHistory


class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = '__all__'


class UserLearningPreferencesSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserLearningPreferences
        fields = '__all__'


class UserLearningHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = UserLearningHistory
        fields = '__all__'