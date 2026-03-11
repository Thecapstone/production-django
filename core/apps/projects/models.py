from typing import TYPE_CHECKING, ClassVar
from django.utils import timezone

from django.db import models
from django.utils.translation import gettext_lazy as _
from core.helpers.models import UIDTimeBasedModel
from core.helpers.enums import ModeratorRolesEnums
from core.helpers.enums import TimerStatus
from .managers import ProjectManager


if TYPE_CHECKING:
    from core.apps.users.models import Moderator  # noqa: TC004


class Project(UIDTimeBasedModel):
    title = models.CharField(max_length=255)
    creator = models.ForeignKey("users.User", on_delete=models.CASCADE, related_name="creator")
    description = models.TextField(_("Description of the Project"), blank=True)
    moderators: models.QuerySet["Moderator"] = models.ForeignKey("users.Moderator", on_delete=models.CASCADE, choices=ModeratorRolesEnums.choices, related_name="project_managers", blank=True)
    members = models.ManyToManyField("users.User", related_name="project_members", blank=True)
    rules = models.TextField(_("Project Rules"), blank=True)
    start_project = models.DateTimeField(default=timezone.now)
    end_project = models.DateTimeField()
    objects: ClassVar[ProjectManager.Manager] = ProjectManager.Manager()
    
    

    @property
    def about(self) -> str:
        return f""" {self.title} is a project created by {self.creator}, it has {(self.moderators).count()} managers, and {(self.members).count()} members
        Description: {self.description}
        Rules: {self.rules}
        """

    def save(self, *args, **kwargs):
        """Override save method to ensure that the creator is always a moderator of the project."""
        project = super().save(*args, **kwargs)
        project.moderators.set(project.creator)
        return project

    def add_moderators(self, moderators: list["Moderator"]) -> None:
        """Add moderators to the project."""
        self.moderators.add(*moderators)

    def remove_moderators(self, moderators: list["Moderator"]) -> None:
        """Remove moderators from the project."""
        self.moderators.remove(*moderators)

    
    def __str__(self):
        return self.title
    
