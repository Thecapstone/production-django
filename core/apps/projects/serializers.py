from django.utils import timezone
from requests import Response
from rest_framework import serializers

from core.apps.posts import models
from .models import Project

from core.apps.users.models import User
from core.helpers.enums import ModeratorRolesEnums


class ProjectSerializer:
    class CreateProject(serializers.ModelSerializer):
        creator = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())
        project_duration = serializers.SerializerMethodField()

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
            while Project.end_project != timezone.now():
                time_left = Project.end_project - timezone.now() 
                return time_left
            raise serializers.ValidationError("Project duration has ended.")
    
        def get_project_duration(self, obj):
            duration = obj.end_project - obj.start_project
            return duration

        def validate_end_project(self, end_project):
            if end_project <= timezone.now():
                raise serializers.ValidationError("End project time must be in the future.")
            return end_project
        

            

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

        def extend_timer(self):
            if Project.start_timer and User == Project.creator:
                Project.end_project== Project.extend_project
                return Response(self.serializer_class("Project duration has been extended"), status=204)
            raise serializers.ValidationError("Only the project creator can extend the project duration.")
        
        class Meta:
            model = Project
            fields = ('title', "about","extend_project", "rules")
