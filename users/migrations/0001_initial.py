# Generated manually for TeamFinder variant 1

import django.utils.timezone
from django.db import migrations, models
import users.models


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        ("auth", "0012_alter_user_first_name_max_length"),
    ]

    operations = [
        migrations.CreateModel(
            name="User",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("password", models.CharField(max_length=128, verbose_name="password")),
                ("last_login", models.DateTimeField(blank=True, null=True, verbose_name="last login")),
                ("is_superuser", models.BooleanField(default=False, help_text="Designates that this user has all permissions without explicitly assigning them.", verbose_name="superuser status")),
                ("email", models.EmailField(max_length=254, unique=True, verbose_name="email")),
                ("name", models.CharField(max_length=124, verbose_name="name")),
                ("surname", models.CharField(max_length=124, verbose_name="surname")),
                ("avatar", models.ImageField(blank=True, upload_to="avatars/", verbose_name="avatar")),
                ("phone", models.CharField(blank=True, db_index=True, default="", max_length=12, verbose_name="phone")),
                ("github_url", models.URLField(blank=True, verbose_name="github_url")),
                ("about", models.TextField(blank=True, max_length=256, verbose_name="about")),
                ("is_active", models.BooleanField(default=True, verbose_name="is_active")),
                ("is_staff", models.BooleanField(default=False, verbose_name="is_staff")),
                ("date_joined", models.DateTimeField(auto_now_add=True, verbose_name="date_joined")),
                ("groups", models.ManyToManyField(blank=True, help_text="The groups this user belongs to. A user will get all permissions granted to each of their groups.", related_name="user_set", related_query_name="user", to="auth.group", verbose_name="groups")),
                ("user_permissions", models.ManyToManyField(blank=True, help_text="Specific permissions for this user.", related_name="user_set", related_query_name="user", to="auth.permission", verbose_name="user permissions")),
            ],
            options={
                "ordering": ["-id"],
            },
            managers=[
                ("objects", users.models.UserManager()),
            ],
        ),
        migrations.AddIndex(
            model_name="user",
            index=models.Index(fields=["email"], name="users_user_email_243f6e_idx"),
        ),
        migrations.AddIndex(
            model_name="user",
            index=models.Index(fields=["phone"], name="users_user_phone_8f5709_idx"),
        ),
    ]
