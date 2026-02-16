from typing import TYPE_CHECKING

from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import UserManager as DjangoUserManager

from django.db.models import Manager as Manager_
from django.db import models

if TYPE_CHECKING:
    from .models import User  # noqa: F401
    from .models import Community  # noqa: F401


class UserManager(DjangoUserManager["User"]):
    """Custom manager for the User model."""

    def _create_user(self, email: str, password: str | None, **extra_fields):
        """
        Create and save a user with the given email and password.
        """
        if not email:
            msg = "The given email must be set"
            raise ValueError(msg)
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.password = make_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email: str, password: str | None = None, **extra_fields):  # type: ignore[override]
        extra_fields.setdefault("is_staff", False)
        extra_fields.setdefault("is_superuser", False)
        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email: str, password: str | None = None, **extra_fields):  # type: ignore[override]
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)

        if extra_fields.get("is_staff") is not True:
            msg = "Superuser must have is_staff=True."
            raise ValueError(msg)
        if extra_fields.get("is_superuser") is not True:
            msg = "Superuser must have is_superuser=True."
            raise ValueError(msg)

        return self._create_user(email, password, **extra_fields)

    def capstone(self, email: str, password: str | None = None, **extra_fields):
        """Create a capstone user with the given email and password."""
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", False)
        return self._create_user(email, password, **extra_fields)


class CommunityManager:

    class Base:
        def create_community(self: models.QuerySet["Community"], title: str, description: str, creator: "User") -> "Community":
            """Create a new community with the given title, description, and creator."""
            community = self.model(title=title, description=description, creator=creator)
            community.save(using=self._db)
            return community

        def update_community(self: models.QuerySet["Community"], community: "Community", title: str | None = None, description: str | None = None, rules: str | None = None) -> "Community":
            """Update the given community with the provided title, description, and rules."""

            if title is not None:
                community.title = title
            if description is not None:
                community.description = description
            if rules is not None:
                community.rules = rules
            community.save(using=self._db)
            return community

        def start_with_x(self: models.QuerySet["Community"], x: str) -> models.QuerySet["Community"]:
            """Return a queryset of communities whose names start with the letter 'A'."""
            return self.filter(name__istartswith=x)

    class Manager(Base, Manager_["Community"]):
        def get_queryset(self) -> models.QuerySet["Community"]:
            return CommunityManager.QuerySet(self.model, using=self._db)

    class QuerySet(models.QuerySet["Community"], Base):
        ...
