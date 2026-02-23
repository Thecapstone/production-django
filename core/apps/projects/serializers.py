from rest_framework import serializers
from .models import Project

class ProjectSerializer(serializers.ModelSerializer):

    class Meta:
        model = Project
        fields = ['title', 'about', 'rules', "start_date", "end_date", 'moderators']

    def create(self, validated_data):
        return Project.objects.create(**validated_data)
    
    def update(self, instance, validated_data):
        instance.title = validated_data.get('title', instance.title)
        instance.about = validated_data.get('about', instance.about)
        instance.rules = validated_data.get('rules', instance.rules)
        instance.save()
        return instance
    
    def creator_as_moderator(self, instance):
        instance.moderators.set(instance.creator)
        return instance