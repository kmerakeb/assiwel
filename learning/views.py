from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from .models import LearningSession, SessionItem, UserProgress, ItemMastery
from .serializers import (
    LearningSessionSerializer, SessionItemSerializer, 
    UserProgressSerializer, ItemMasterySerializer
)


# Learning Session Views
class LearningSessionListCreateView(generics.ListCreateAPIView):
    queryset = LearningSession.objects.all()
    serializer_class = LearningSessionSerializer
    permission_classes = [IsAuthenticated]


class LearningSessionDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = LearningSession.objects.all()
    serializer_class = LearningSessionSerializer
    permission_classes = [IsAuthenticated]


# Session Item Views
class SessionItemListCreateView(generics.ListCreateAPIView):
    queryset = SessionItem.objects.all()
    serializer_class = SessionItemSerializer
    permission_classes = [IsAuthenticated]


class SessionItemDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = SessionItem.objects.all()
    serializer_class = SessionItemSerializer
    permission_classes = [IsAuthenticated]


# User Progress Views
class UserProgressListCreateView(generics.ListCreateAPIView):
    queryset = UserProgress.objects.all()
    serializer_class = UserProgressSerializer
    permission_classes = [IsAuthenticated]


class UserProgressDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = UserProgress.objects.all()
    serializer_class = UserProgressSerializer
    permission_classes = [IsAuthenticated]


# Item Mastery Views
class ItemMasteryListCreateView(generics.ListCreateAPIView):
    queryset = ItemMastery.objects.all()
    serializer_class = ItemMasterySerializer
    permission_classes = [IsAuthenticated]


class ItemMasteryDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = ItemMastery.objects.all()
    serializer_class = ItemMasterySerializer
    permission_classes = [IsAuthenticated]
