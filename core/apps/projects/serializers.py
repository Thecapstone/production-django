from django.utils import timezone
from requests import Response
from rest_framework import serializers
from .models import Project

from core.apps.users.models import User
from core.helpers.enums import ModeratorRolesEnums


class ProjectSerializer:
    class CreateProject(serializers.ModelSerializer):
        creator = serializers.PrimaryKeyRelatedField(queryset=User.objects.all)
        end_project = serializers.DateTimeField()
        start_project = serializers.DateTimeField()


        class Meta:
            model = Project
            fields = ["title", "creator","start_project","end_project","description", "rules"]
    
        def validate_project_title(self, title):
            """
            ensure that a user cannot create a project with the same name as an existing project.
            """
            if Project.objects.filter(title__iexact=title).exists():
                raise serializers.ValidationError("A project with this name already exists.")
            return title
    
        def start_timer(self):
            while self.end_project != timezone.now():
                time_left = self.end_project - timezone.now() 
                return time_left
            return Response (self.serializer_class("Project duration has ended."), status=204)
    
        def extend_timer(self):
            if self.start_timer and User == self.creator:
                self.end_project== self.extend_project
                return Response(self.serializer_class("Project duration has been extended"), status=204)
        
        def project_duration(self):
            duration = self.end_project - self.start_project
            return duration

            

    class ProjectDetail(serializers.ModelSerializer):
        detail = serializers.SerializerMethodField()
        communities = Project.objects.prefetch_related('questions_and_answers', 'idea_threads', 'long_drafts')
        posts = Project.objects.prefetch_related('questions_and_answers', 'idea_threads', 'long_drafts')

        def get_detail(self, obj):
            return (f"{obj.title} project by {obj.creator}")
    
        class Meta:
            model = Project
            fields = ('about','moderators', 'detail', 'communities', 'posts')

    
    class ProjectList(serializers.ModelSerializer):
        class Meta:
            model = Project
            exclude = ['about', 'members', 'rules']

        
    class ProjectUpdateSerializer(serializers.ModelSerializer):
        extend_project = serializers.DateTimeField()
        class Meta:
            model = Project
            fields = ('title', "about","extend_project", "rules")
