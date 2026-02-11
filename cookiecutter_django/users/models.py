
from typing import ClassVar

from django.contrib.auth.models import AbstractUser
from django.db import models
from django.urls import reverse
from django.utils.translation import gettext_lazy as _

from cookiecutter_django.utils.enums import CommentReportReason, CommunityReportReason, ModeratorRoles
from cookiecutter_django.utils.models import UIDTimeBasedModel

from .managers import UserManager


class User(AbstractUser):
    """
    Default custom user model for cookiecutter-django.
    If adding fields that need to be filled at user signup,
    check forms.SignupForm and forms.SocialSignupForms accordingly.
    """

    # First and last name do not cover name patterns around the globe
    name = models.CharField(_("Name of User"), blank=True, max_length=255)
    first_name = None  # type: ignore[assignment]
    last_name = None  # type: ignore[assignment]
    email = models.EmailField(_("email address"), unique=True)
    username = None  # type: ignore[assignment]

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    objects: ClassVar[UserManager] = UserManager()

    def get_absolute_url(self) -> str:
        """Get URL for user's detail view.

        Returns:
            str: URL for user detail.

        """
        return reverse("users:detail", kwargs={"pk": self.id})
    
class ModeratorPermission(UIDTimeBasedModel):
    role = models.CharField(_("Tag of Permission"), choices=ModeratorRoles.choices, blank=False, max_length=255, unique=True)
    name = models.CharField(_("Name of Permission"), blank=False, max_length=255)
    emoji = models.CharField(_("Emoji for Permission"), blank=True, max_length=10)

    def __str__(self) -> str:
        return self.name

class Moderator(UIDTimeBasedModel):
    user = models.ForeignKey("users.User", on_delete=models.CASCADE, related_name="moderator_user")
    permissions = models.ManyToManyField("users.ModeratorPermission", related_name="moderator_permissions")

class Community(UIDTimeBasedModel):
    name = models.CharField(_("Name of Community"), blank=False, max_length=255)
    admin = models.ForeignKey("users.User", on_delete=models.CASCADE, related_name="admin")
    sub_admins = models.ManyToManyField("users.User", related_name="sub_admins", blank=True)
    moderators = models.ManyToManyField("users.User", related_name="moderators", blank=True)
    members = models.ManyToManyField("users.User", related_name="members", blank=True)
    description = models.TextField(_("Description of Community"), blank=True)
    rules = models.TextField(_("Rules of Community"), blank=True)
    emoji = models.CharField(_("Emoji for Community"), blank=True, max_length=10)

    def __str__(self) -> str:
        return self.name

    def about(self) -> str:
        return f"""{self.name} is a community managed by {self.admin.name}.
        It has {self.moderators.count()} moderators and {self.members.count()} members.
        Description: {self.description}
        Rules: {self.rules}
        """
class Project(UIDTimeBasedModel):
    name = models.CharField(_("Name of Project"), blank=False, max_length=255)
    description = models.TextField(_("Description of Project"), blank=True)
    creator = models.ForeignKey('users.User', on_delete=models.CASCADE, related_name='project_creator')
    managers = models.ManyToManyField('users,User', related_name='project_managers', blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    last_updated = models. DateTimeField(auto_now=True)

    @classmethod
    def open_project(cls, name, description, creator, managers=None):
        """
        Creates and returns a new project
        """
        project = cls.objects.create(name=name, description=description, creator=creator)
        if managers:
            project.managers.set(managers)
        
        return project
    
    def close_project(self):
        """Deletes this project."""

        self.delete()

    def __str__(self):
        return self.name
    

class ReportComment(UIDTimeBasedModel):
    reporter = models.ForeignKey("users.User", on_delete=models.CASCADE, related_name="reporter")
    reported_user = models.ForeignKey("users.User", on_delete=models.CASCADE, related_name="reported_user")
    reason_tag = models.CharField(_("Tag of Report"), choices=CommentReportReason.choices, blank=False, max_length=255)
    reason = models.TextField(_("Reason for Report"), blank=False)
    community = models.ForeignKey("users.Community", on_delete=models.CASCADE, related_name="report_community", null=True, blank=True)

    # Generic content point to the post
    content_type = models.ForeignKey("contenttypes.ContentType", on_delete=models.CASCADE, null=True, blank=True)
    object_id = models.CharField(max_length=255, blank=True)

    def __str__(self) -> str:
        return f"Report by {self.reporter.name} against {self.reported_user.name} for reason: {self.reason}"

class ReportCommunity(UIDTimeBasedModel):
    reporter = models.ForeignKey("users.User", on_delete=models.CASCADE, related_name="community_reporter")
    community = models.ForeignKey("users.Community", on_delete=models.CASCADE, related_name="reported_community")
    reason_tag = models.CharField(_("Tag of Report"), choices=CommunityReportReason.choices, blank=False, max_length=255)
    reason = models.TextField(_("Reason for Report"), blank=False)

    def __str__(self) -> str:
        return f"Report by {self.reporter.name} against: {self.community.name} for: {self.reason}"
    

