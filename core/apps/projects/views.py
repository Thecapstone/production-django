from rest_framework import viewsets, request
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from django.utils import timezone

from .models import Project
from .serializers import ProjectSerializer

class ProjectViewSet(viewsets.ModelViewSet):
    queryset = Project.objects.all()
    serializer_class = ProjectSerializer
    permission_classes = [AllowAny]

    def start_timer(self):
        while Project.end_project != timezone.now():
            time_left = self.end_project - timezone.now() 
            return time_left
        return Response (self.serializer_class("Project duration has ended."), status=204)
    
    def extend_timer(self):
        if self.start_timer and request.user == Project.creator:
            Project.end_project== Project.extend_project
            Project.save
            return Response(self.serializer_class("Project duration has been extended"), status=204)
