from rest_framework import generics, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import (
    Organization, User, Profile, Category, SubCategory, Topic, 
    LearningPath, VocabularyItem, ListeningItem, SpeakingItem, 
    MultipleChoiceItem, AuditLog, AnalyticsEvent
)
from .serializers import (
    OrganizationSerializer, UserSerializer, ProfileSerializer, 
    CategorySerializer, SubCategorySerializer, TopicSerializer, 
    LearningPathSerializer, VocabularyItemSerializer, 
    ListeningItemSerializer, SpeakingItemSerializer, 
    MultipleChoiceItemSerializer, AuditLogSerializer, 
    AnalyticsEventSerializer
)


# Organization Views
class OrganizationListCreateView(generics.ListCreateAPIView):
    queryset = Organization.objects.all()
    serializer_class = OrganizationSerializer
    permission_classes = [IsAuthenticated]


class OrganizationDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Organization.objects.all()
    serializer_class = OrganizationSerializer
    permission_classes = [IsAuthenticated]


# User Views
class UserListCreateView(generics.ListCreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]


class UserDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]


# Profile Views
class ProfileDetailView(generics.RetrieveUpdateAPIView):
    queryset = Profile.objects.all()
    serializer_class = ProfileSerializer
    permission_classes = [IsAuthenticated]


# Category Views
class CategoryListCreateView(generics.ListCreateAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [IsAuthenticated]


class CategoryDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [IsAuthenticated]


# SubCategory Views
class SubCategoryListCreateView(generics.ListCreateAPIView):
    queryset = SubCategory.objects.all()
    serializer_class = SubCategorySerializer
    permission_classes = [IsAuthenticated]


class SubCategoryDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = SubCategory.objects.all()
    serializer_class = SubCategorySerializer
    permission_classes = [IsAuthenticated]


# Topic Views
class TopicListCreateView(generics.ListCreateAPIView):
    queryset = Topic.objects.all()
    serializer_class = TopicSerializer
    permission_classes = [IsAuthenticated]


class TopicDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Topic.objects.all()
    serializer_class = TopicSerializer
    permission_classes = [IsAuthenticated]


# Learning Path Views
class LearningPathListCreateView(generics.ListCreateAPIView):
    queryset = LearningPath.objects.all()
    serializer_class = LearningPathSerializer
    permission_classes = [IsAuthenticated]


class LearningPathDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = LearningPath.objects.all()
    serializer_class = LearningPathSerializer
    permission_classes = [IsAuthenticated]


# Learning Item Views
class VocabularyItemListCreateView(generics.ListCreateAPIView):
    queryset = VocabularyItem.objects.all()
    serializer_class = VocabularyItemSerializer
    permission_classes = [IsAuthenticated]


class VocabularyItemDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = VocabularyItem.objects.all()
    serializer_class = VocabularyItemSerializer
    permission_classes = [IsAuthenticated]


class ListeningItemListCreateView(generics.ListCreateAPIView):
    queryset = ListeningItem.objects.all()
    serializer_class = ListeningItemSerializer
    permission_classes = [IsAuthenticated]


class ListeningItemDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = ListeningItem.objects.all()
    serializer_class = ListeningItemSerializer
    permission_classes = [IsAuthenticated]


class SpeakingItemListCreateView(generics.ListCreateAPIView):
    queryset = SpeakingItem.objects.all()
    serializer_class = SpeakingItemSerializer
    permission_classes = [IsAuthenticated]


class SpeakingItemDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = SpeakingItem.objects.all()
    serializer_class = SpeakingItemSerializer
    permission_classes = [IsAuthenticated]


class MultipleChoiceItemListCreateView(generics.ListCreateAPIView):
    queryset = MultipleChoiceItem.objects.all()
    serializer_class = MultipleChoiceItemSerializer
    permission_classes = [IsAuthenticated]


class MultipleChoiceItemDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = MultipleChoiceItem.objects.all()
    serializer_class = MultipleChoiceItemSerializer
    permission_classes = [IsAuthenticated]


# Audit Log Views
class AuditLogListCreateView(generics.ListCreateAPIView):
    queryset = AuditLog.objects.all()
    serializer_class = AuditLogSerializer
    permission_classes = [IsAuthenticated]


class AuditLogDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = AuditLog.objects.all()
    serializer_class = AuditLogSerializer
    permission_classes = [IsAuthenticated]


# Analytics Event Views
class AnalyticsEventListCreateView(generics.ListCreateAPIView):
    queryset = AnalyticsEvent.objects.all()
    serializer_class = AnalyticsEventSerializer
    permission_classes = [IsAuthenticated]


class AnalyticsEventDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = AnalyticsEvent.objects.all()
    serializer_class = AnalyticsEventSerializer
    permission_classes = [IsAuthenticated]


# Health check endpoint
@api_view(['GET'])
def health_check(request):
    return Response({'status': 'healthy', 'message': 'API is running'}, status=status.HTTP_200_OK)
