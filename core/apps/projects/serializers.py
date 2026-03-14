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
    
        def get_project_duration(self, obj):
            duration = obj.end_project - obj.start_project
            return duration

        def validate_end_project(self, end_project):
            if end_project <= timezone.now():
                raise serializers.ValidationError("End project time must be in the future.")
            return end_project
            

    class ProjectDetail(serializers.ModelSerializer):
        detail = serializers.SerializerMethodField()
        about = serializers.SerializerMethodField()
        project_duration = serializers.SerializerMethodField()

        def get_about(self, obj):
            return f""" {obj.title}, is a project by {obj.creator}, with {(obj.members).count()} members currently.
            Here's a brief description on what to expect and how to contribute {obj.description}
            Rules: {obj.rules}
            """

        def get_detail(self, obj):
            return (f"{obj.title} project by {obj.creator}")
        
        def get_project_duration(self, obj):
            duration = obj.end_project - obj.start_project
            return duration
    
        class Meta:
            model = Project
            fields = ('title','creator','created_at', 'project_duration', 'about', 'detail', 'project_communities')


    class ProjectList(serializers.ModelSerializer):
        class Meta:
            model = Project
            fields = ['description', 'members', 'rules']

        
    class ProjectUpdateSerializer(serializers.ModelSerializer):
        
        class Meta:
            model = Project
            fields = ('title', "about","extend_project", "rules")
