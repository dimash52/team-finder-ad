from django.conf import settings
from django.db import models


PROJECT_NAME_MAX_LENGTH = 200
PROJECT_STATUS_MAX_LENGTH = 6

PROJECT_STATUS_OPEN = "open"
PROJECT_STATUS_CLOSED = "closed"
PROJECT_STATUS_CHOICES = (
    (PROJECT_STATUS_OPEN, "Open"),
    (PROJECT_STATUS_CLOSED, "Closed"),
)


class Project(models.Model):
    STATUS_OPEN = PROJECT_STATUS_OPEN
    STATUS_CLOSED = PROJECT_STATUS_CLOSED
    STATUS_CHOICES = PROJECT_STATUS_CHOICES

    name = models.CharField("name", max_length=PROJECT_NAME_MAX_LENGTH)
    description = models.TextField("description", blank=True)
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="owned_projects",
        verbose_name="owner",
    )
    created_at = models.DateTimeField(
        "created_at", auto_now_add=True, db_index=True)
    github_url = models.URLField("github_url", blank=True)
    status = models.CharField(
        "status",
        max_length=PROJECT_STATUS_MAX_LENGTH,
        choices=PROJECT_STATUS_CHOICES,
        default=PROJECT_STATUS_OPEN,
        db_index=True,
    )
    participants = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        related_name="participated_projects",
        blank=True,
        verbose_name="participants",
    )

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["-created_at"]),
            models.Index(fields=["status"]),
        ]

    def __str__(self) -> str:
        return self.name
