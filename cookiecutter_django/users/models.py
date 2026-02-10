
from typing import ClassVar

from django.contrib.auth.models import AbstractUser
from django.db import models
from django.urls import reverse
from django.utils.translation import gettext_lazy as _

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
    
    name = models.CharField(_("Name of Permission"), blank=False, max_length=255)

    def __str__(self) -> str:
        return self.name

class Moderator(UIDTimeBasedModel):
    user = models.ForeignKey("user.User", on_delete=models.CASCADE, related_name="moderator_user")
    permissions = models.ManyToManyField("user.ModeratorPermission", related_name="moderator_permissions")

class Community(UIDTimeBasedModel):
    name = models.CharField(_("Name of Community"), blank=False, max_length=255)
    admin = models.ForeignKey("user.User", on_delete=models.CASCADE, related_name="admin")
    moderators = models.ManyToManyField("user.User", related_name="moderators", blank=True)
    members = models.ManyToManyField("user.User", related_name="members", blank=True)
    """
    One to Many/ForeignKey: One instance only
    Many to Many: Multiple instances
    """

    def __str__(self) -> str:
        return self.name