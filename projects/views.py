from __future__ import annotations

from http import HTTPStatus

from django.contrib.auth.decorators import login_required
from django.http import HttpRequest, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from team_finder.utils import paginate_queryset

from .forms import ProjectForm
from .models import Project


PROJECTS_PER_PAGE = 12
AUTH_REQUIRED_STATUS = "auth_required"
FORBIDDEN_STATUS = "forbidden"
ERROR_STATUS = "error"
OK_STATUS = "ok"
LOGIN_URL = "/users/login/"


def _project_queryset():
    return (
        Project.objects.select_related("owner")
        .prefetch_related("participants")
        .order_by("-created_at")
    )


def index(request: HttpRequest):
    return redirect("projects:list")


def project_list(request: HttpRequest):
    projects = paginate_queryset(
        request, _project_queryset(), PROJECTS_PER_PAGE)
    return render(request, "projects/project_list.html", {"projects": projects})


@login_required(login_url="users:login")
def favorite_projects(request: HttpRequest):
    projects_qs = (
        request.user.favorites.select_related("owner")
        .prefetch_related("participants")
        .order_by("-created_at")
    )
    projects = paginate_queryset(request, projects_qs, PROJECTS_PER_PAGE)
    return render(request, "projects/favorite_projects.html", {"projects": projects})


def project_detail(request: HttpRequest, pk: int):
    project = get_object_or_404(
        Project.objects.select_related(
            "owner").prefetch_related("participants"),
        pk=pk,
    )
    return render(request, "projects/project-details.html", {"project": project})


@login_required(login_url="users:login")
def create_project(request: HttpRequest):
    if request.method == "POST":
        form = ProjectForm(request.POST)
        if form.is_valid():
            project = form.save(commit=False)
            project.owner = request.user
            project.save()
            project.participants.add(request.user)
            return redirect("projects:detail", pk=project.pk)
    else:
        form = ProjectForm(initial={"status": Project.STATUS_OPEN})

    return render(
        request,
        "projects/create-project.html",
        {"form": form, "is_edit": False},
    )


@login_required(login_url="users:login")
def edit_project(request: HttpRequest, pk: int):
    project = get_object_or_404(Project, pk=pk)
    if project.owner_id != request.user.id and not request.user.is_staff:
        return redirect("projects:detail", pk=project.pk)

    if request.method == "POST":
        form = ProjectForm(request.POST, instance=project)
        if form.is_valid():
            project = form.save()
            owner_is_participant = project.participants.filter(
                pk=project.owner_id,
            ).exists()
            if project.owner_id and not owner_is_participant:
                project.participants.add(project.owner)
            return redirect("projects:detail", pk=project.pk)
    else:
        form = ProjectForm(instance=project)

    return render(
        request,
        "projects/create-project.html",
        {"form": form, "is_edit": True},
    )


@require_POST
def complete_project(request: HttpRequest, pk: int):
    if not request.user.is_authenticated:
        return JsonResponse(
            {"status": AUTH_REQUIRED_STATUS},
            status=HTTPStatus.UNAUTHORIZED,
        )

    project = get_object_or_404(Project, pk=pk)
    if project.owner_id != request.user.id and not request.user.is_staff:
        return JsonResponse(
            {"status": FORBIDDEN_STATUS},
            status=HTTPStatus.FORBIDDEN,
        )

    if project.status != Project.STATUS_OPEN:
        return JsonResponse(
            {"status": ERROR_STATUS, "project_status": project.status},
            status=HTTPStatus.BAD_REQUEST,
        )

    project.status = Project.STATUS_CLOSED
    project.save(update_fields=["status"])
    return JsonResponse(
        {"status": OK_STATUS, "project_status": Project.STATUS_CLOSED},
    )


@require_POST
def toggle_participate(request: HttpRequest, pk: int):
    if not request.user.is_authenticated:
        return JsonResponse(
            {"status": AUTH_REQUIRED_STATUS},
            status=HTTPStatus.UNAUTHORIZED,
        )

    project = get_object_or_404(Project, pk=pk)
    if project.owner_id == request.user.id:
        if not project.participants.filter(pk=request.user.pk).exists():
            project.participants.add(request.user)
        return JsonResponse({"status": OK_STATUS, "participant": True})

    if project.participants.filter(pk=request.user.pk).exists():
        project.participants.remove(request.user)
        participant = False
    else:
        project.participants.add(request.user)
        participant = True

    return JsonResponse({"status": OK_STATUS, "participant": participant})


@require_POST
def toggle_favorite(request: HttpRequest, pk: int):
    if not request.user.is_authenticated:
        return JsonResponse(
            {"status": AUTH_REQUIRED_STATUS, "login_url": LOGIN_URL},
            status=HTTPStatus.UNAUTHORIZED,
        )

    project = get_object_or_404(Project, pk=pk)
    if request.user.favorites.filter(pk=project.pk).exists():
        request.user.favorites.remove(project)
        favorited = False
    else:
        request.user.favorites.add(project)
        favorited = True

    return JsonResponse({"status": OK_STATUS, "favorited": favorited})
