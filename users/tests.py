from django.test import TestCase
from django.urls import reverse

from projects.models import Project
from users.forms import ProfileForm
from users.models import User


REGISTER_URL_NAME = "users:register"
PROJECTS_LIST_URL_NAME = "projects:list"
USERS_LIST_URL_NAME = "users:list"

NAME_FIELD = "name"
SURNAME_FIELD = "surname"
EMAIL_FIELD = "email"
PASSWORD_FIELD = "password"
ABOUT_FIELD = "about"
PHONE_FIELD = "phone"
GITHUB_URL_FIELD = "github_url"
FILTER_FIELD = "filter"

TEST_PASSWORD = "pass12345"

IVAN_NAME = "Ivan"
IVAN_SURNAME = "Ivanov"
IVAN_EMAIL = "ivan@example.com"

FIRST_USER_EMAIL = "one@example.com"
FIRST_USER_NAME = "One"
SECOND_USER_EMAIL = "two@example.com"
SECOND_USER_NAME = "Two"
USER_SURNAME = "User"

OWNER_EMAIL = "owner@example.com"
OWNER_NAME = "Owner"
PARTICIPANT_EMAIL = "participant@example.com"
PARTICIPANT_NAME = "Participant"
PARTICIPANT_FULL_NAME = "Participant User"

FIRST_USER_PHONE = "+70000000001"
FIRST_USER_PHONE_LEGACY_FORMAT = "80000000001"
EMPTY_PHONE = ""
OWNER_PHONE = "+70000000003"
PARTICIPANT_PHONE = "+70000000004"

EMPTY_ABOUT = ""
GITHUB_URL = "https://github.com/teamfinder"

PROJECT_NAME = "Owner project"
PARTICIPANTS_OF_MY_PROJECTS_FILTER = "participants-of-my-projects"


class UserFlowTests(TestCase):
    def test_registration_creates_user_and_logs_in(self):
        response = self.client.post(
            reverse(REGISTER_URL_NAME),
            {
                NAME_FIELD: IVAN_NAME,
                SURNAME_FIELD: IVAN_SURNAME,
                EMAIL_FIELD: IVAN_EMAIL,
                PASSWORD_FIELD: TEST_PASSWORD,
            },
        )

        self.assertRedirects(response, reverse(PROJECTS_LIST_URL_NAME))
        self.assertTrue(User.objects.filter(email=IVAN_EMAIL).exists())

    def test_phone_normalization_and_duplicate_validation(self):
        User.objects.create_user(
            email=FIRST_USER_EMAIL,
            password=TEST_PASSWORD,
            name=FIRST_USER_NAME,
            surname=USER_SURNAME,
            phone=FIRST_USER_PHONE,
        )
        user = User.objects.create_user(
            email=SECOND_USER_EMAIL,
            password=TEST_PASSWORD,
            name=SECOND_USER_NAME,
            surname=USER_SURNAME,
            phone=EMPTY_PHONE,
        )
        form = ProfileForm(
            data={
                NAME_FIELD: SECOND_USER_NAME,
                SURNAME_FIELD: USER_SURNAME,
                ABOUT_FIELD: EMPTY_ABOUT,
                PHONE_FIELD: FIRST_USER_PHONE_LEGACY_FORMAT,
                GITHUB_URL_FIELD: GITHUB_URL,
            },
            instance=user,
        )

        self.assertFalse(form.is_valid())
        self.assertIn(PHONE_FIELD, form.errors)

    def test_variant_one_user_filter_participants_of_my_projects(self):
        owner = User.objects.create_user(
            email=OWNER_EMAIL,
            password=TEST_PASSWORD,
            name=OWNER_NAME,
            surname=USER_SURNAME,
            phone=OWNER_PHONE,
        )
        participant = User.objects.create_user(
            email=PARTICIPANT_EMAIL,
            password=TEST_PASSWORD,
            name=PARTICIPANT_NAME,
            surname=USER_SURNAME,
            phone=PARTICIPANT_PHONE,
        )
        project = Project.objects.create(
            name=PROJECT_NAME,
            owner=owner,
            status=Project.STATUS_OPEN,
        )
        project.participants.add(owner, participant)
        self.client.force_login(owner)

        response = self.client.get(
            reverse(USERS_LIST_URL_NAME),
            {FILTER_FIELD: PARTICIPANTS_OF_MY_PROJECTS_FILTER},
        )

        self.assertContains(response, PARTICIPANT_FULL_NAME)
