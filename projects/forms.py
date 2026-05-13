from urllib.parse import urlparse

from django import forms

from .models import Project


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
            "description": forms.Textarea(attrs={"rows": 6}),
            "github_url": forms.URLInput(attrs={"placeholder": "https://github.com/owner/repository"}),
            "status": forms.Select(choices=[("open", "Открыт"), ("closed", "Закрыт")]),
        }

    def clean_github_url(self):
        url = (self.cleaned_data.get("github_url") or "").strip()
        if not url:
            return url
        parsed = urlparse(url)
        host = (parsed.netloc or "").lower()
        if host not in {"github.com", "www.github.com"}:
            raise forms.ValidationError("Ссылка должна вести на GitHub.")
        return url
