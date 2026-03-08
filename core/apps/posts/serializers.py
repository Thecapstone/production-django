from rest_framework import serializers
from . import managers
from .models import IdeaThread
from core.helpers.enums import CommentReportReason

class EagerLoadingMixin:
    @classmethod
    def setup_eager_loading(cls, queryset):
        if hasattr(cls, "SELECT"):
            queryset = queryset.select_related(*cls.SELECT)
        if hasattr(cls, "PREFETCH"):
            queryset = queryset.prefetch_related(*cls.PREFETCH)

class PostsSerializer:
    class CreateQuestionAndAnswerSerializer(serializers.ModelSerializer):
        class Meta:
            model = managers.QuestionAndAnswer
            fields = ("title", "content", "choices", 'tags', 'community', 'project')
    
    class CreateIdeaThreadSerializer(serializers.ModelSerializer):
        class Meta:
            model = managers.QuestionAndAnswer
            fields = ( "content", 'community','tags', 'project')
    
    class CreateLongDraftSerializer(serializers.ModelSerializer):
        class Meta:
            model = managers.QuestionAndAnswer
            fields = ("title", "content",'tags', 'community', 'project')


    class ReportPostSerializer(serializers.ModelSerializer):
        reason = serializers.ChoiceField(choices=CommentReportReason)
        detail = serializers.Charfield(required=True)
        post_id = serializers.CharField()

        class Meta:
            model = IdeaThread
            fields = ("reason", "detail")