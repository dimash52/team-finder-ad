from __future__ import annotations

from django.contrib.auth import login, logout, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import PasswordChangeForm
from django.core.paginator import Paginator
from django.db.models import Q
from django.http import HttpRequest
from django.shortcuts import get_object_or_404, redirect, render

from .forms import LoginForm, ProfileForm, RegisterForm, TeamFinderPasswordChangeForm
from .models import User

USERS_PER_PAGE = 12


FILTERS = {
    "owners-of-favorite-projects",
    "owners-of-participating-projects",
    "interested-in-my-projects",
    "participants-of-my-projects",
}


def register(request: HttpRequest):
    if request.user.is_authenticated:
        return redirect("projects:list")

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
    if request.user.is_authenticated:
        return redirect("projects:list")

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
        User.objects.prefetch_related("owned_projects", "owned_projects__participants"),
        pk=pk,
        is_active=True,
    )
    return render(request, "users/user-details.html", {"user": participant})


def user_list(request: HttpRequest):
    participants_qs = User.objects.filter(is_active=True).order_by("-id")
    active_filter = request.GET.get("filter")

    if request.user.is_authenticated and active_filter in FILTERS:
        if active_filter == "owners-of-favorite-projects":
            participants_qs = participants_qs.filter(owned_projects__in=request.user.favorites.all())
        elif active_filter == "owners-of-participating-projects":
            participants_qs = participants_qs.filter(owned_projects__participants=request.user)
        elif active_filter == "interested-in-my-projects":
            participants_qs = participants_qs.filter(favorites__owner=request.user)
        elif active_filter == "participants-of-my-projects":
            participants_qs = participants_qs.filter(participated_projects__owner=request.user)
        participants_qs = participants_qs.distinct().order_by("-id")
    else:
        active_filter = None

    page = Paginator(participants_qs, USERS_PER_PAGE).get_page(request.GET.get("page"))
    return render(request, "users/participants.html", {"participants": page, "active_filter": active_filter})


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
