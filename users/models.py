from __future__ import annotations

from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.db import models

from team_finder.utils import generate_initial_avatar

from .managers import UserManager


USER_NAME_MAX_LENGTH = 124
USER_SURNAME_MAX_LENGTH = 124
USER_PHONE_MAX_LENGTH = 12
USER_ABOUT_MAX_LENGTH = 256

USER_AVATAR_UPLOAD_TO = "avatars/"

USER_EMAIL_VERBOSE_NAME = "email"
USER_NAME_VERBOSE_NAME = "name"
USER_SURNAME_VERBOSE_NAME = "surname"
USER_AVATAR_VERBOSE_NAME = "avatar"
USER_PHONE_VERBOSE_NAME = "phone"
USER_GITHUB_VERBOSE_NAME = "github_url"
USER_ABOUT_VERBOSE_NAME = "about"
USER_IS_ACTIVE_VERBOSE_NAME = "is_active"
USER_IS_STAFF_VERBOSE_NAME = "is_staff"
USER_DATE_JOINED_VERBOSE_NAME = "date_joined"
USER_FAVORITES_VERBOSE_NAME = "favorites"

PROJECT_MODEL_REFERENCE = "projects.Project"

OWNED_PROJECTS_RELATED_NAME = "owned_projects"
FAVORITES_RELATED_NAME = "interested_users"

USERNAME_FIELD_NAME = "email"
EMAIL_FIELD_NAME = "email"

REQUIRED_FIELDS = ["name", "surname"]


class User(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(USER_EMAIL_VERBOSE_NAME, unique=True)
    name = models.CharField(USER_NAME_VERBOSE_NAME,
                            max_length=USER_NAME_MAX_LENGTH)
    surname = models.CharField(
        USER_SURNAME_VERBOSE_NAME,
        max_length=USER_SURNAME_MAX_LENGTH,
    )
    avatar = models.ImageField(
        USER_AVATAR_VERBOSE_NAME,
        upload_to=USER_AVATAR_UPLOAD_TO,
        blank=True,
    )
    phone = models.CharField(
        USER_PHONE_VERBOSE_NAME,
        max_length=USER_PHONE_MAX_LENGTH,
        blank=True,
        default="",
        db_index=True,
    )
    github_url = models.URLField(USER_GITHUB_VERBOSE_NAME, blank=True)
    about = models.TextField(
        USER_ABOUT_VERBOSE_NAME,
        max_length=USER_ABOUT_MAX_LENGTH,
        blank=True,
    )
    favorites = models.ManyToManyField(
        PROJECT_MODEL_REFERENCE,
        related_name=FAVORITES_RELATED_NAME,
        blank=True,
        verbose_name=USER_FAVORITES_VERBOSE_NAME,
    )
    is_active = models.BooleanField(USER_IS_ACTIVE_VERBOSE_NAME, default=True)
    is_staff = models.BooleanField(USER_IS_STAFF_VERBOSE_NAME, default=False)
    date_joined = models.DateTimeField(
        USER_DATE_JOINED_VERBOSE_NAME,
        auto_now_add=True,
    )

    objects = UserManager()

    USERNAME_FIELD = USERNAME_FIELD_NAME
    REQUIRED_FIELDS = REQUIRED_FIELDS
    EMAIL_FIELD = EMAIL_FIELD_NAME

    class Meta:
        ordering = ["-id"]
        indexes = [
            models.Index(fields=["email"]),
            models.Index(fields=["phone"]),
        ]

    def save(self, *args, **kwargs):
        if not self.avatar and self.name:
            self.avatar = generate_initial_avatar(self.name, self.email)

        super().save(*args, **kwargs)

    def __str__(self) -> str:
        return f"{self.name} {self.surname}".strip()
