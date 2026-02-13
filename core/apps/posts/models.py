from typing import Self
from django.db import models

from django.contrib.postgres.fields import ArrayField


class QuestionAndAnswer(models.Model):
    """
    Survey-based structure discussion
    Story:
        As a writer, I want to ask structured questions about my work so that I can receive targeted 
        feedback.
    """
    title = models.CharField(max_length=255)
    community = models.ForeignKey("users.Community", default=None, null=True, blank=True, on_delete=models.SET_NULL, related_name="questions")
    original = models.BooleanField(default=False)  # False if this is the original question, False if it's a reply
    user = models.ForeignKey("users.User", on_delete=models.CASCADE, related_name="questions")
    choices = ArrayField(models.CharField(max_length=255))  # List of choices for the question
    """["Choice 1", "Choice 2", "Choice 3"]"""
    replies = models.ForeignKey("self", on_delete=models.CASCADE, related_name="question_replies", blank=True, null=True)
    upvotes = models.IntegerField(default=0)
    downvotes = models.IntegerField(default=0)
    most_helpful = models.ForeignKey("self", on_delete=models.SET_NULL, related_name="most_helpful_reply", blank=True, null=True)

    @property
    def bookmark_count(self) -> int:
        from core.apps.users.models import User
        return User.objects.filter(booksmarks=self.id).count()


class IdeaThread(models.Model):
    """
    Idea Threads (Default Short-Form Threading)
    Story:
        As a basic-tier user, I want to share creative ideas even if I must break them
        into multiple posts.
    """
    content = models.CharField(max_length=250)
    original = models.BooleanField(default=False)  # False if this is the original post, False if it's a reply
    community = models.ForeignKey("users.Community", default=None, null=True, blank=True, on_delete=models.SET_NULL, related_name="idea_threads")
    user = models.ForeignKey("users.User", on_delete=models.CASCADE, related_name="idea_threads")
    likes = models.IntegerField(default=0)
    comments = models.ForeignKey("self", on_delete=models.CASCADE, related_name="idea_thread_comments", blank=True, null=True)


class LongDraft(models.Model):
    """
    Article-based discussions
    
    Story: As a premium writer, I want to publish complete drafts without breaking them into parts.
    """
    user = models.ForeignKey("users.User", on_delete=models.CASCADE, related_name="long_draft")
    title = models.CharField(max_length=255)
    content = models.TextField()
    community = models.ForeignKey("users.community", default=None, null=True, on_delete=models.SET_NULL, related_name="long_draft")
    comment = models.ForeignKey("self", on_delete=models.CASCADE, related_name="long_draft_comments", blank=True, null=True, max_length=400)
    likes = models.IntegerField(default=0)

class bookmark(models.Model):
    """
    Bookmarking System
    Story:
        As a user, I want to bookmark questions and threads so that I can easily find them later.
    """
    user = models.ForeignKey("users.User", on_delete=models.CASCADE, related_name="bookmarks")
    question = models.ForeignKey("QuestionAndAnswer", on_delete=models.CASCADE, related_name="bookmarked_questions", blank=True, null=True)
    idea_thread = models.ForeignKey("IdeaThread", on_delete=models.CASCADE, related_name="bookmarked_idea_threads", blank=True, null=True)
    long_draft = models.ForeignKey("LongDraft", on_delete=models.CASCADE, related_name="bookmarked_long_drafts", blank=True, null=True)