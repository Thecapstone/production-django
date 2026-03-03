from rest_framework import serializers

from core.apps.posts.models import QuestionAndAnswer
from core.apps.users.models import User


class UserSerializer(serializers.ModelSerializer[User]):
    class Meta:
        model = User
        fields = ["name", "url"]

        extra_kwargs = {
            "url": {"view_name": "api:user-detail", "lookup_field": "pk"},
        }


class PostSerializers:

    class BaseQuestionAndAnswerSerializer(serializers.ModelSerializer):
        class Meta:
            model = QuestionAndAnswer
            fields = ["title", "content"]

    
    class IdeaThreadSerializer(serializers.ModelSerializer):
        class Meta:
            model = QuestionAndAnswer
            fields = ["id", "content"]

    class LongDraftSerializer(serializers.ModelSerializer):
        class Meta:
            model = QuestionAndAnswer
            fields = ["id", "content"]


class QuestionAndAnswerSerializer:


    class CreateQuestionAndAnswerSerializer(PostSerializers.BaseQuestionAndAnswerSerializer):
        class Meta(PostSerializers.BaseQuestionAndAnswerSerializer.Meta):
            ...

    class DetailQuestionAndAnswerSerializer(PostSerializers.BaseQuestionAndAnswerSerializer):
        class Meta(PostSerializers.BaseQuestionAndAnswerSerializer.Meta):
            fields = [*PostSerializers.BaseQuestionAndAnswerSerializer.Meta.fields, "downvotes", "upvotes"]

    


    