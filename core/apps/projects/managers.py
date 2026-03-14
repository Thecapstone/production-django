from typing import TYPE_CHECKING, ClassVar
from django.db.models import Manager as Manager_
from django.db import models
from django.db.models import QuerySet
from django.utils import timezone


if TYPE_CHECKING:
    from core.apps.projects.models import Project
    from core.apps.users.models import User



class ProjectManager:

    class Base:
        def open_project(self: models.QuerySet["Project"], title: str, creator:"User", description: str, start_project: timezone.datetime, end_project: timezone.datetime, rules: str) -> "Project":
            """ Creates a new project with the given title, creator, about, and moderators."""
            project: "Project" = self.model(title=title, creator=creator, description=description, start_project=start_project, end_project=end_project, rules=rules)

            project.save(using=self._db)
            #project.moderators.set(project.creator)
            return project


        def update_project(self: models.QuerySet["Project"], project: "Project", extend_project: timezone.datetime | None=None, title: str | None=None, description: str | None=None, rules: str | None=None) -> "Project":
            """updates a project title, rules, or about fields with new information."""

            if title is not None:
                project.title = title
            
            if extend_project is not None:
                project.end_project = extend_project
            
            if description is not None:
                project.about = description

            if rules is not None:
                project.rules = rules
            
            project.save(using=self._db)
            return project
        
        def starts_with_x(self: models.QuerySet["Project"], x: str) -> models.QuerySet["Project"]:
            """Return all projects that start with the given string."""
            return self.filter(title__startswith=x)
        
        def filter_by_creator(self: models.QuerySet["Project"], creator: "User") -> models.QuerySet["Project"]:
            """Returns all projects created by a given user"""
            return self.filter(creator=creator).values_list('title', flat=True)

        def close_project(self: models.QuerySet["Project"], project: "Project") -> None:
            """ Deletes/Closes a project"""
            project.delete()

    class Manager(Base, Manager_["Project"]):
        def get_queryset(self) -> QuerySet:
            return ProjectManager.QuerySet_(self.model, using=self._db)

    class QuerySet_(Base, QuerySet):
        ...
        