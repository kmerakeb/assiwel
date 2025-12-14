from rest_framework import serializers
from .models import AIModel, AIPromptTemplate, AIInteraction, AISafetyFilter, AICache, AIUsageMetering


class AIModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = AIModel
        fields = '__all__'


class AIPromptTemplateSerializer(serializers.ModelSerializer):
    class Meta:
        model = AIPromptTemplate
        fields = '__all__'


class AIInteractionSerializer(serializers.ModelSerializer):
    class Meta:
        model = AIInteraction
        fields = '__all__'


class AISafetyFilterSerializer(serializers.ModelSerializer):
    class Meta:
        model = AISafetyFilter
        fields = '__all__'


class AICacheSerializer(serializers.ModelSerializer):
    class Meta:
        model = AICache
        fields = '__all__'


class AIUsageMeteringSerializer(serializers.ModelSerializer):
    class Meta:
        model = AIUsageMetering
        fields = '__all__'