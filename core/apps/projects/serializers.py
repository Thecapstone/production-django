from rest_framework import serializers
from .models import Project

from core.apps.users.models.User import User
from core.utils.enums import ModeratorRoles


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
            
    class ProjectList(serializers.ModelSerializer):
        detail = serializers.SerializerMethodField()

        def get_detail(self, obj):
            return (f"{obj.title} project by {obj.creator}")
        
        class Meta:
            model = Project
            fields = ('__all__', 'detail')

        
    class ProjectUpdateSerializer(serializers.ModelSerilizers):
        model = Project
        fields = ('title', "about", "rules")

