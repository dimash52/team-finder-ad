from django import forms

from team_finder.utils import validate_github_url

from .models import Project


PROJECT_DESCRIPTION_ROWS = 6
GITHUB_PLACEHOLDER = "https://github.com/owner/repository"
PROJECT_STATUS_FORM_CHOICES = (
    (Project.STATUS_OPEN, "Открыт"),
    (Project.STATUS_CLOSED, "Закрыт"),
)


class ProjectForm(forms.ModelForm):
    class Meta:
        model = Project
        fields = ("name", "description", "github_url", "status")
        labels = {
            "name": "Название проекта",
            "description": "Описание проекта",
            "github_url": "GitHub",
            "status": "Статус",
        }
        widgets = {
            "description": forms.Textarea(attrs={"rows": PROJECT_DESCRIPTION_ROWS}),
            "github_url": forms.URLInput(attrs={"placeholder": GITHUB_PLACEHOLDER}),
            "status": forms.Select(choices=PROJECT_STATUS_FORM_CHOICES),
        }

    def clean_github_url(self):
        return validate_github_url(self.cleaned_data.get("github_url", ""))
