from django.test import TestCase
from django.urls import reverse

from projects.models import Project
from users.forms import ProfileForm
from users.models import User


class UserFlowTests(TestCase):
    def test_registration_creates_user_and_logs_in(self):
        response = self.client.post(
            reverse("users:register"),
            {
                "name": "Ivan",
                "surname": "Ivanov",
                "email": "ivan@example.com",
                "password": "pass12345",
            },
        )
        self.assertRedirects(response, reverse("projects:list"))
        self.assertTrue(User.objects.filter(email="ivan@example.com").exists())

    def test_phone_normalization_and_duplicate_validation(self):
        user1 = User.objects.create_user(
            email="one@example.com",
            password="pass12345",
            name="One",
            surname="User",
            phone="+70000000001",
        )
        user2 = User.objects.create_user(
            email="two@example.com",
            password="pass12345",
            name="Two",
            surname="User",
            phone="",
        )
        form = ProfileForm(
            data={
                "name": "Two",
                "surname": "User",
                "about": "",
                "phone": "80000000001",
                "github_url": "https://github.com/teamfinder",
            },
            instance=user2,
        )
        self.assertFalse(form.is_valid())
        self.assertIn("phone", form.errors)

    def test_variant_one_user_filter_participants_of_my_projects(self):
        owner = User.objects.create_user(
            email="owner@example.com",
            password="pass12345",
            name="Owner",
            surname="User",
            phone="+70000000003",
        )
        participant = User.objects.create_user(
            email="participant@example.com",
            password="pass12345",
            name="Participant",
            surname="User",
            phone="+70000000004",
        )
        project = Project.objects.create(name="Owner project", owner=owner, status="open")
        project.participants.add(owner, participant)
        self.client.force_login(owner)

        response = self.client.get(reverse("users:list"), {"filter": "participants-of-my-projects"})
        self.assertContains(response, "Participant User")
