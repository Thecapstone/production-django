from rest_framework import serializers
from . import managers
from .models import IdeaThread
from core.helpers.enums import CommentReportReason

class PostsSerializer:
    class CreateQuestionAndAnswerSerializer(serializers.ModelSerializer):
        class Meta:
            model = managers.QuestionAndAnswer
            fields = ("title", "content", "choices", 'community', 'project')


    class ReportPostSerializer(serializers.ModelSerializer):
        reason = serializers.ChoiceField(choices=CommentReportReason)
        detail = serializers.Charfield(required=True)
        post_id = serializers.CharField()

        class Meta:
            model = IdeaThread
            fields = ("reason", "detail")