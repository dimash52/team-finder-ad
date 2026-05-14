from __future__ import annotations

from django import forms
from django.contrib.auth import authenticate, get_user_model
from django.contrib.auth.forms import PasswordChangeForm, ReadOnlyPasswordHashField

from team_finder.utils import clean_phone, validate_github_url


User = get_user_model()

PROFILE_ABOUT_ROWS = 4
PROFILE_ABOUT_MAX_LENGTH = 256

PHONE_PLACEHOLDER = "+7XXXXXXXXXX"
GITHUB_PLACEHOLDER = "https://github.com/username"

INVALID_LOGIN_ERROR = "Неверный имейл или пароль"
INACTIVE_ACCOUNT_ERROR = "Аккаунт заблокирован"
PASSWORD_MISMATCH_ERROR = "Passwords don't match"


class RegisterForm(forms.ModelForm):
    password = forms.CharField(
        label="Пароль",
        widget=forms.PasswordInput(attrs={"autocomplete": "new-password"}),
    )

    class Meta:
        model = User
        fields = ("name", "surname", "email", "password")
        labels = {
            "name": "Имя",
            "surname": "Фамилия",
            "email": "Email",
        }
        widgets = {
            "name": forms.TextInput(attrs={"placeholder": "Имя"}),
            "surname": forms.TextInput(attrs={"placeholder": "Фамилия"}),
            "email": forms.EmailInput(attrs={"placeholder": "Email", "autocomplete": "email"}),
        }

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password"])

        if commit:
            user.save()

        return user


class LoginForm(forms.Form):
    email = forms.EmailField(
        label="Email",
        widget=forms.EmailInput(attrs={"autocomplete": "email"}),
    )
    password = forms.CharField(
        label="Пароль",
        widget=forms.PasswordInput(attrs={"autocomplete": "current-password"}),
    )

    def __init__(self, request=None, *args, **kwargs):
        self.request = request
        self.user_cache = None
        super().__init__(*args, **kwargs)

    def clean(self):
        cleaned_data = super().clean()
        email = cleaned_data.get("email")
        password = cleaned_data.get("password")

        if email and password:
            self.user_cache = authenticate(
                self.request,
                username=email,
                password=password,
            )
            if self.user_cache is None:
                raise forms.ValidationError(INVALID_LOGIN_ERROR)

            if not self.user_cache.is_active:
                raise forms.ValidationError(INACTIVE_ACCOUNT_ERROR)

        return cleaned_data

    def get_user(self):
        return self.user_cache


class ProfileForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ("name", "surname", "avatar", "about", "phone", "github_url")
        labels = {
            "name": "Имя",
            "surname": "Фамилия",
            "avatar": "Аватар",
            "about": "О себе",
            "phone": "Телефон",
            "github_url": "GitHub",
        }
        widgets = {
            "about": forms.Textarea(
                attrs={
                    "rows": PROFILE_ABOUT_ROWS,
                    "maxlength": PROFILE_ABOUT_MAX_LENGTH,
                }
            ),
            "phone": forms.TextInput(attrs={"placeholder": PHONE_PLACEHOLDER}),
            "github_url": forms.URLInput(attrs={"placeholder": GITHUB_PLACEHOLDER}),
        }

    def clean_phone(self):
        return clean_phone(
            self.cleaned_data.get("phone", ""),
            User,
            self.instance,
        )

    def clean_github_url(self):
        return validate_github_url(self.cleaned_data.get("github_url", ""))


class TeamFinderPasswordChangeForm(PasswordChangeForm):
    pass


class UserCreationAdminForm(forms.ModelForm):
    password1 = forms.CharField(
        label="Password",
        widget=forms.PasswordInput,
    )
    password2 = forms.CharField(
        label="Password confirmation",
        widget=forms.PasswordInput,
    )

    class Meta:
        model = User
        fields = (
            "email",
            "name",
            "surname",
            "phone",
            "github_url",
            "about",
            "is_active",
            "is_staff",
        )

    def clean_password2(self):
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")

        if password1 and password2 and password1 != password2:
            raise forms.ValidationError(PASSWORD_MISMATCH_ERROR)

        return password2

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password1"])

        if commit:
            user.save()
            self.save_m2m()

        return user


class UserChangeAdminForm(forms.ModelForm):
    password = ReadOnlyPasswordHashField()

    class Meta:
        model = User
        fields = (
            "email",
            "password",
            "name",
            "surname",
            "avatar",
            "phone",
            "github_url",
            "about",
            "favorites",
            "is_active",
            "is_staff",
            "is_superuser",
            "groups",
            "user_permissions",
        )
