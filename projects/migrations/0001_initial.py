# Generated manually for TeamFinder variant 1

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="Project",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("name", models.CharField(max_length=200, verbose_name="name")),
                ("description", models.TextField(blank=True, verbose_name="description")),
                ("created_at", models.DateTimeField(auto_now_add=True, db_index=True, verbose_name="created_at")),
                ("github_url", models.URLField(blank=True, verbose_name="github_url")),
                ("status", models.CharField(choices=[("open", "Open"), ("closed", "Closed")], db_index=True, default="open", max_length=6, verbose_name="status")),
                ("owner", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="owned_projects", to=settings.AUTH_USER_MODEL, verbose_name="owner")),
                ("participants", models.ManyToManyField(blank=True, related_name="participated_projects", to=settings.AUTH_USER_MODEL, verbose_name="participants")),
            ],
            options={
                "ordering": ["-created_at"],
            },
        ),
        migrations.AddIndex(
            model_name="project",
            index=models.Index(fields=["-created_at"], name="projects_pr_created_45e6b5_idx"),
        ),
        migrations.AddIndex(
            model_name="project",
            index=models.Index(fields=["status"], name="projects_pr_status_52eb8c_idx"),
        ),
    ]
