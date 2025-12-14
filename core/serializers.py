from rest_framework import serializers
from .models import (
    Organization, User, Profile, Category, SubCategory, Topic, 
    LearningPath, VocabularyItem, ListeningItem, SpeakingItem, 
    MultipleChoiceItem, AuditLog, AnalyticsEvent
)
from django.contrib.auth.password_validation import validate_password


class OrganizationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Organization
        fields = '__all__'


class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, validators=[validate_password])
    
    class Meta:
        model = User
        fields = (
            'id', 'username', 'email', 'first_name', 'last_name', 
            'role', 'organization', 'avatar', 'is_active', 'date_joined',
            'password', 'last_login'
        )
        read_only_fields = ('id', 'date_joined', 'last_login')
    
    def create(self, validated_data):
        password = validated_data.pop('password')
        user = User(**validated_data)
        user.set_password(password)
        user.save()
        return user


class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = '__all__'


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = '__all__'


class SubCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = SubCategory
        fields = '__all__'


class TopicSerializer(serializers.ModelSerializer):
    class Meta:
        model = Topic
        fields = '__all__'


class LearningPathSerializer(serializers.ModelSerializer):
    class Meta:
        model = LearningPath
        fields = '__all__'


class VocabularyItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = VocabularyItem
        fields = '__all__'


class ListeningItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = ListeningItem
        fields = '__all__'


class SpeakingItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = SpeakingItem
        fields = '__all__'


class MultipleChoiceItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = MultipleChoiceItem
        fields = '__all__'


class AuditLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = AuditLog
        fields = '__all__'


class AnalyticsEventSerializer(serializers.ModelSerializer):
    class Meta:
        model = AnalyticsEvent
        fields = '__all__'