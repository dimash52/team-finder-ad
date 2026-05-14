from django.core.management.base import BaseCommand

from projects.models import Project
from users.models import User


class Command(BaseCommand):
    help = "Create demo users and projects for manual TeamFinder checks."

    def handle(self, *args, **options):
        demo_users = [
            ("anna@example.com", "Анна", "Смирнова", "+70000000011"),
            ("pavel@example.com", "Павел", "Кузнецов", "+70000000012"),
            ("maria@example.com", "Мария", "Попова", "+70000000013"),
        ]
        users = []
        for email, name, surname, phone in demo_users:
            user, created = User.objects.get_or_create(
                email=email,
                defaults={
                    "name": name,
                    "surname": surname,
                    "phone": phone,
                    "about": "Участник TeamFinder",
                },
            )
            if created:
                user.set_password("demo12345")
                user.save()
            users.append(user)

        for index, user in enumerate(users, start=1):
            project, _ = Project.objects.get_or_create(
                name=f"Демо-проект {index}",
                owner=user,
                defaults={
                    "description": "Pet-проект для проверки функциональности TeamFinder.",
                    "github_url": "https://github.com/",
                    "status": Project.STATUS_OPEN,
                },
            )
            project.participants.add(user)

        users[0].favorites.add(Project.objects.exclude(owner=users[0]).first())
        self.stdout.write(
            self.style.SUCCESS("Demo data created. Password for all demo users: demo12345")
        )
