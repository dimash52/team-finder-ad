from django.test import Client, TestCase
from django.urls import reverse

from projects.models import Project
from users.models import User


class ProjectFlowTests(TestCase):
    def setUp(self):
        self.owner = User.objects.create_user(
            email="owner@example.com",
            password="pass12345",
            name="Owner",
            surname="User",
            phone="+70000000001",
        )
        self.member = User.objects.create_user(
            email="member@example.com",
            password="pass12345",
            name="Member",
            surname="User",
            phone="+70000000002",
        )
        self.project = Project.objects.create(name="Test project", owner=self.owner, status="open")
        self.project.participants.add(self.owner)

    def test_project_list_available_for_guest(self):
        response = self.client.get(reverse("projects:list"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Test project")

    def test_authenticated_user_can_toggle_favorite(self):
        self.client.force_login(self.member)
        response = self.client.post(reverse("projects:toggle_favorite", args=[self.project.pk]))
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.json()["favorited"])
        self.assertTrue(self.member.favorites.filter(pk=self.project.pk).exists())

    def test_owner_can_complete_project(self):
        self.client.force_login(self.owner)
        response = self.client.post(reverse("projects:complete", args=[self.project.pk]))
        self.assertEqual(response.status_code, 200)
        self.project.refresh_from_db()
        self.assertEqual(self.project.status, Project.STATUS_CLOSED)

    def test_participation_toggle(self):
        self.client.force_login(self.member)
        response = self.client.post(reverse("projects:toggle_participate", args=[self.project.pk]))
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.json()["participant"])
        self.assertTrue(self.project.participants.filter(pk=self.member.pk).exists())
