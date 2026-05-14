from http import HTTPStatus

from django.test import TestCase
from django.urls import reverse

from projects.models import Project
from users.models import User


OWNER_EMAIL = "owner@example.com"
MEMBER_EMAIL = "member@example.com"
TEST_PASSWORD = "pass12345"

OWNER_NAME = "Owner"
MEMBER_NAME = "Member"
USER_SURNAME = "User"

OWNER_PHONE = "+70000000001"
MEMBER_PHONE = "+70000000002"

PROJECT_NAME = "Test project"

FAVORITED_RESPONSE_KEY = "favorited"
PARTICIPANT_RESPONSE_KEY = "participant"


class ProjectFlowTests(TestCase):
    def setUp(self):
        self.owner = User.objects.create_user(
            email=OWNER_EMAIL,
            password=TEST_PASSWORD,
            name=OWNER_NAME,
            surname=USER_SURNAME,
            phone=OWNER_PHONE,
        )
        self.member = User.objects.create_user(
            email=MEMBER_EMAIL,
            password=TEST_PASSWORD,
            name=MEMBER_NAME,
            surname=USER_SURNAME,
            phone=MEMBER_PHONE,
        )
        self.project = Project.objects.create(
            name=PROJECT_NAME,
            owner=self.owner,
            status=Project.STATUS_OPEN,
        )
        self.project.participants.add(self.owner)

    def test_project_list_available_for_guest(self):
        response = self.client.get(reverse("projects:list"))

        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertContains(response, PROJECT_NAME)

    def test_authenticated_user_can_toggle_favorite(self):
        self.client.force_login(self.member)

        response = self.client.post(reverse("projects:toggle_favorite", args=[self.project.pk]))

        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertTrue(response.json()[FAVORITED_RESPONSE_KEY])
        self.assertTrue(self.member.favorites.filter(pk=self.project.pk).exists())

    def test_owner_can_complete_project(self):
        self.client.force_login(self.owner)

        response = self.client.post(reverse("projects:complete", args=[self.project.pk]))

        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.project.refresh_from_db()
        self.assertEqual(self.project.status, Project.STATUS_CLOSED)

    def test_participation_toggle(self):
        self.client.force_login(self.member)

        response = self.client.post(reverse("projects:toggle_participate", args=[self.project.pk]))

        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertTrue(response.json()[PARTICIPANT_RESPONSE_KEY])
        self.assertTrue(self.project.participants.filter(pk=self.member.pk).exists())
