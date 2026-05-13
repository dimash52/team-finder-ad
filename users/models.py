from __future__ import annotations

import random
import uuid
from io import BytesIO

from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.core.files.base import ContentFile
from django.db import models


class UserManager(BaseUserManager):
    """Manager for the email-based TeamFinder user model."""

    use_in_migrations = True

    def _create_user(self, email: str, password: str | None, **extra_fields):
        if not email:
            raise ValueError("Email is required")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email: str, password: str | None = None, **extra_fields):
        extra_fields.setdefault("is_staff", False)
        extra_fields.setdefault("is_superuser", False)
        extra_fields.setdefault("is_active", True)
        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email: str, password: str | None = None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_active", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True.")

        extra_fields.setdefault("name", "Admin")
        extra_fields.setdefault("surname", "User")
        return self._create_user(email, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField("email", unique=True)
    name = models.CharField("name", max_length=124)
    surname = models.CharField("surname", max_length=124)
    avatar = models.ImageField("avatar", upload_to="avatars/", blank=True)
    phone = models.CharField("phone", max_length=12, blank=True, default="", db_index=True)
    github_url = models.URLField("github_url", blank=True)
    about = models.TextField("about", max_length=256, blank=True)
    favorites = models.ManyToManyField(
        "projects.Project",
        related_name="interested_users",
        blank=True,
        verbose_name="favorites",
    )
    is_active = models.BooleanField("is_active", default=True)
    is_staff = models.BooleanField("is_staff", default=False)
    date_joined = models.DateTimeField("date_joined", auto_now_add=True)

    objects = UserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["name", "surname"]
    EMAIL_FIELD = "email"

    class Meta:
        ordering = ["-id"]
        indexes = [
            models.Index(fields=["email"]),
            models.Index(fields=["phone"]),
        ]

    def __str__(self) -> str:
        return f"{self.name} {self.surname}".strip() or self.email

    @property
    def full_name(self) -> str:
        return f"{self.name} {self.surname}".strip()

    def save(self, *args, **kwargs):
        if not self.avatar and self.name:
            self._generate_initial_avatar()
        super().save(*args, **kwargs)

    def _generate_initial_avatar(self) -> None:
        """Generate a simple readable avatar with the first letter of the name."""
        from PIL import Image, ImageDraw, ImageFont

        palette = ["#E9D5FF", "#BFDBFE", "#BBF7D0", "#FDE68A", "#FBCFE8", "#DDD6FE"]
        bg_color = random.choice(palette)
        image_size = 256
        image = Image.new("RGB", (image_size, image_size), bg_color)
        draw = ImageDraw.Draw(image)
        letter = (self.name[:1] or self.email[:1] or "U").upper()

        try:
            font = ImageFont.truetype("DejaVuSans-Bold.ttf", 128)
        except OSError:
            font = ImageFont.load_default()

        bbox = draw.textbbox((0, 0), letter, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
        position = ((image_size - text_width) / 2, (image_size - text_height) / 2 - 8)
        draw.text(position, letter, fill="#111827", font=font)

        buffer = BytesIO()
        image.save(buffer, format="PNG")
        filename = f"avatar_{uuid.uuid4()}.png"
        self.avatar.save(filename, ContentFile(buffer.getvalue()), save=False)
