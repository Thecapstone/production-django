from rest_framework import serializers
from .models import Project

from core.apps.users.models.User import User
from core.utils.enums import ModeratorRoles


class ProjectSerializer:
    class CreateProject(serializers.ModelSerializer):
        title = serializers.SerializerMethodField()
        moderators = serializers.ChoiceField(choices=ModeratorRoles.choices, required=False, default=Project.creator)
        creator = serializers.PrimaryKeyRelatedField(queryset=User.objects.all)

        def get_title(self, obj):
            return (f"{obj.title} project by {obj.creator}")
        
        class Meta:
            model = Project
            fields = ["title", "creator", "about", "rules"]
    
    def validate_project_name(serializers.Serializer):
        """
        ensure that a user cannot create a project with the same name as an existing project.
        """
        if Project.objects.filter(title__iexact=serializers.validated_data["title"]).exists():
            raise serializers.ValidationError("A project with this name already exists.")
