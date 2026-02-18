from typing import ClassVar

from django.db import models
from django.utils.translation import gettext_lazy as _
from core.utils.models import UIDTimeBasedModel
from core.utils.enums import ModeratorRoles
from .managers import ProjectManager



class Project(UIDTimeBasedModel):
    title = models.CharField(max_length=255)
    creator = models.ForeignKey("users.User", on_delete=models.CASCADE, related_name="creator")
    about = models.TextField(_("Description of the Project"), blank=True)
    moderators = models.ForeignKey("users.Moderator", on_delete=models.CASCADE, choices=ModeratorRoles.choices, related_name="project_managers", blank=True)
    members = models.ManyToManyField("users.User", related_name="project_members", blank=True)
    rules = models.TextField(_("Project Rules"), blank=True)
    objects: ClassVar[ProjectManager.Manager] = ProjectManager.Manager()

    def about(self) -> str:
        return f""" {self.title} is a project created by {self.creator}, it has {(self.moderators).count()} managers, and {(self.members).count()} members
        Description: {self.about}
        Rules: {self.rules}
        """
    
    
    def __str__(self):
        return self.title

