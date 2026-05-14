from __future__ import annotations

from django.contrib.auth import login, logout, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.http import HttpRequest
from django.shortcuts import get_object_or_404, redirect, render

from team_finder.utils import paginate_queryset

from .forms import LoginForm, ProfileForm, RegisterForm, TeamFinderPasswordChangeForm
from .models import User


USERS_PER_PAGE = 12

FILTER_OWNERS_OF_FAVORITE_PROJECTS = "owners-of-favorite-projects"
FILTER_OWNERS_OF_PARTICIPATING_PROJECTS = "owners-of-participating-projects"
FILTER_INTERESTED_IN_MY_PROJECTS = "interested-in-my-projects"
FILTER_PARTICIPANTS_OF_MY_PROJECTS = "participants-of-my-projects"

USER_FILTERS = {
    FILTER_OWNERS_OF_FAVORITE_PROJECTS,
    FILTER_OWNERS_OF_PARTICIPATING_PROJECTS,
    FILTER_INTERESTED_IN_MY_PROJECTS,
    FILTER_PARTICIPANTS_OF_MY_PROJECTS,
}


def register(request: HttpRequest):
    if request.method == "POST":
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect("projects:list")
    else:
        form = RegisterForm()

    return render(request, "users/register.html", {"form": form})


def login_view(request: HttpRequest):
    if request.method == "POST":
        form = LoginForm(request, data=request.POST)
        if form.is_valid():
            login(request, form.get_user())
            return redirect("projects:list")
    else:
        form = LoginForm(request)

    return render(request, "users/login.html", {"form": form})


def logout_view(request: HttpRequest):
    logout(request)
    return redirect("projects:list")


def user_detail(request: HttpRequest, pk: int):
    participant = get_object_or_404(
        User.objects.prefetch_related("owned_projects"),
        pk=pk,
        is_active=True,
    )
    return render(request, "users/user-details.html", {"user": participant})


def user_list(request: HttpRequest):
    participants_qs = User.objects.filter(is_active=True).order_by("-id")
    active_filter = request.GET.get("filter")

    if request.user.is_authenticated and active_filter in USER_FILTERS:
        if active_filter == FILTER_OWNERS_OF_FAVORITE_PROJECTS:
            participants_qs = participants_qs.filter(
                owned_projects__in=request.user.favorites.all(),
            )
        elif active_filter == FILTER_OWNERS_OF_PARTICIPATING_PROJECTS:
            participants_qs = participants_qs.filter(
                owned_projects__participants=request.user,
            )
        elif active_filter == FILTER_INTERESTED_IN_MY_PROJECTS:
            participants_qs = participants_qs.filter(
                favorites__owner=request.user,
            )
        elif active_filter == FILTER_PARTICIPANTS_OF_MY_PROJECTS:
            participants_qs = participants_qs.filter(
                participated_projects__owner=request.user,
            )

        participants_qs = participants_qs.distinct()

    participants = paginate_queryset(request, participants_qs, USERS_PER_PAGE)

    return render(
        request,
        "users/participants.html",
        {
            "participants": participants,
            "active_filter": active_filter,
        },
    )


@login_required(login_url="users:login")
def edit_profile(request: HttpRequest):
    if request.method == "POST":
        form = ProfileForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            return redirect("users:detail", pk=request.user.pk)
    else:
        form = ProfileForm(instance=request.user)

    return render(request, "users/edit_profile.html", {"form": form})


@login_required(login_url="users:login")
def change_password(request: HttpRequest):
    if request.method == "POST":
        form = TeamFinderPasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)
            return redirect("users:detail", pk=request.user.pk)
    else:
        form = TeamFinderPasswordChangeForm(request.user)

    return render(request, "users/change_password.html", {"form": form})
