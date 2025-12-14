from rest_framework import serializers
from .models import ContentAuthoring, LearningItemTag, LearningItemResource, ContentFeedback, ContentUsageStats


class ContentAuthoringSerializer(serializers.ModelSerializer):
    class Meta:
        model = ContentAuthoring
        fields = '__all__'


class LearningItemTagSerializer(serializers.ModelSerializer):
    class Meta:
        model = LearningItemTag
        fields = '__all__'


class LearningItemResourceSerializer(serializers.ModelSerializer):
    class Meta:
        model = LearningItemResource
        fields = '__all__'


class ContentFeedbackSerializer(serializers.ModelSerializer):
    class Meta:
        model = ContentFeedback
        fields = '__all__'


class ContentUsageStatsSerializer(serializers.ModelSerializer):
    class Meta:
        model = ContentUsageStats
        fields = '__all__'