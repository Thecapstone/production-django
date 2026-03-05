from rest_framework import serializers
from .models import Project

from core.apps.users.models import User
from core.helpers.enums import ModeratorRolesEnums


class ProjectSerializer:
    class CreateProject(serializers.ModelSerializer):
        creator = serializers.PrimaryKeyRelatedField(queryset=User.objects.all)
        
        class Meta:
            model = Project
            fields = ["title", "creator","about", "rules"]
    
        def validate_project_title(self, title):
            """
            ensure that a user cannot create a project with the same name as an existing project.
            """
            if Project.objects.filter(title__iexact=title).exists():
                raise serializers.ValidationError("A project with this name already exists.")
            return title
            

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
        class Meta:
            model = Project
            fields = ('title', "about", "rules")
