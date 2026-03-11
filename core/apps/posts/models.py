from typing import Self, ClassVar
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models
import auto_prefetch

from django.contrib.postgres.fields import ArrayField
from core.helpers.models import UIDTimeBasedModel

from .managers import PostsManager

class Bookmark(UIDTimeBasedModel):
    """
    Users can bookmark any content (questions, idea threads, or long drafts) for easy access later.
    """

    user = models.ForeignKey("users.User", on_delete=models.CASCADE, related_name="bookmarks") #many-to-one
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE) #one-to-one
    object_id = models.CharField()
    content_object = GenericForeignKey("content_type", "object_id")

    class Meta(auto_prefetch.Model.Meta):
        unique_together = ("user", "content_type", "object_id")

class PostTags(UIDTimeBasedModel):
    """
    Users can create tags for their posts, structuring how they are found or filtered.
    """
    user = models.ForeignKey("users.User", on_delete=models.CASCADE, related_name="post_tags") #many-to-one
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE) #many-to-one
    object_id = models.CharField()
    content_object = GenericForeignKey("content_type", "object_id")


class BaseContent(UIDTimeBasedModel):
    """
    Base model for content containing all common post fields
    """
    parent = models.ForeignKey("self", on_delete=models.CASCADE, related_name="replies", blank=True, null=True)

    class Meta(auto_prefetch.Model.Meta):
        abstract = True

    @property
    def bookmark_count(self) -> int:
        content_type = ContentType.objects.get_for_model(self)
        return Bookmark.objects.filter(content_type=content_type, object_id=self.id).count()


class QuestionAndAnswer(BaseContent):
    """
    Survey-based structure discussion
    Story:
        As a writer, I want to ask structured questions about my work so that I can receive targeted 
        feedback.
    """
    title = models.CharField(max_length=255)
    content = models.CharField(max_length=250)
    original = models.BooleanField(default=False)  # True if this is the original question, False if it's a reply
    choices = ArrayField(models.CharField(max_length=255), null=True, blank=True)  # List of choices for the question
    """["Choice 1", "Choice 2", "Choice 3"]"""
    upvotes = models.IntegerField(default=0)
    community = models.ForeignKey("users.Community", on_delete=models.SET_NULL, null=True, blank=True, related_name="question_and_answer") #many-to-one
    project = models.ForeignKey("projects.Project", blank=True, null=True, on_delete=models.SET_NULL, related_name="question_and_answer") # many-to-one
    user = models.ForeignKey("users.User", on_delete=models.CASCADE, related_name="question_and_answer_user")
    
    downvotes = models.IntegerField(default=0)
    most_helpful = models.ForeignKey("self", on_delete=models.SET_NULL, related_name="most_helpful_reply", blank=True, null=True)

    objects = ClassVar[PostsManager.QuestionAndAnswerManager]


class IdeaThread(BaseContent):
    """
    Idea Threads (Default Short-Form Threading)
    Story:
        As a basic-tier user, I want to share creative ideas even if I must break them
        into multiple posts.
    """
    
    content = models.CharField(max_length=250)
    original = models.BooleanField(default=False)  # True if this is the original post, False if it's a reply
    likes = models.IntegerField(default=0)
    community = models.ForeignKey("users.Community", on_delete=models.SET_NULL, null=True, blank=True, related_name="idea_threads")
    project = models.ForeignKey("projects.Project", blank=True, null=True, on_delete=models.SET_NULL, related_name="idea_threads")
    user = models.ForeignKey("users.User", on_delete=models.CASCADE, related_name="idea_threads_user")

    objects = ClassVar[PostsManager.IdeaThreadManager]



class LongDraft(BaseContent):
    """
    Article-based discussions

    Story: As a premium writer, I want to publish complete drafts without breaking them into parts.
    """
    title = models.CharField(max_length=255)
    content = models.TextField()
    likes = models.IntegerField(default=0)
    community = models.ForeignKey("users.Community", on_delete=models.SET_NULL, null=True, blank=True, related_name="long_drafts")
    project = models.ForeignKey("projects.Project", blank=True, null=True, on_delete=models.SET_NULL, related_name="long_drafts")
    user = models.ForeignKey("users.User", on_delete=models.CASCADE, related_name="long_drafts_user")
    objects = ClassVar[PostsManager.LongDraftManager]

