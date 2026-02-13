from typing import Self
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models

from django.contrib.postgres.fields import ArrayField

class Bookmark(models.Model):
    """
    Users can bookmark any content (questions, idea threads, or long drafts) for easy access later.
    """

    users = models.ForeignKey("users.User", on_delete=models.CASCADE, related_name="bookmarks")

    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.positiveIntegerField()
    content_object = GenericForeignKey("content_type", "object_id")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("users", "content_type", "object_id")

class BaseContent(models.Model):
    """
    Base model for content containing all common fields
    """
    user = models.ForeignKey("users.User", on_delete=models.CASCADE, related_name="author")
    community = models.ForeignKey("users.Community", on_delete=models.SET_NULL, null=True, blank=True, related_name="content_community")
    parent = models.ForeignKey("self", on_delete=models.CASCADE, related_name="replies", blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True

    @property
    def bookmark_count(self) -> int:
        content_type = ContentType.objects.get_for_model(self)
        return Bookmark.objects.filter(content_type=content_type, object_id = self.id).count()


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
    choices = ArrayField(models.CharField(max_length=255))  # List of choices for the question
    """["Choice 1", "Choice 2", "Choice 3"]"""
    upvotes = models.IntegerField(default=0)
    downvotes = models.IntegerField(default=0)
    most_helpful = models.ForeignKey("self", on_delete=models.SET_NULL, related_name="most_helpful_reply", blank=True, null=True)

    #@property
    #def bookmark_count(self) -> int:
        #from core.apps.users.models import User
        #return User.objects.filter(booksmarks=self.id).count()


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


class LongDraft(BaseContent):
    """
    Article-based discussions
    
    Story: As a premium writer, I want to publish complete drafts without breaking them into parts.
    """
    title = models.CharField(max_length=255)
    content = models.TextField()
    likes = models.IntegerField(default=0)
