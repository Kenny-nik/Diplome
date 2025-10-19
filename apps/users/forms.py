from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm, PasswordChangeForm

from .models import Profile

User = get_user_model()
USERNAME_FIELD = User.USERNAME_FIELD


class CustomUserCreationForm(UserCreationForm):
    """Форма регистрации, работает и с USERNAME_FIELD=email, и с username."""
    email = forms.EmailField(required=True, label="E-mail")

    class Meta(UserCreationForm.Meta):
        model = User
        if USERNAME_FIELD == "email":
            fields = ("email",)
        else:
            fields = ("username", "email")


class ProfileForm(forms.ModelForm):
    email = forms.EmailField(disabled=True, required=False, label="E-mail")

    class Meta:
        model = User
        fields = ("first_name", "last_name", "email")
        labels = {
            "first_name": "Имя",
            "last_name": "Фамилия",
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # добавим bootstrap-классы
        for name in ("first_name", "last_name", "email"):
            if name in self.fields:
                self.fields[name].widget.attrs.setdefault("class", "form-control")


class AvatarForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ("avatar",)
        labels = {"avatar": "Аватар"}
        widgets = {
            "avatar": forms.ClearableFileInput(attrs={"class": "form-control"})
        }


class StyledPasswordChangeForm(PasswordChangeForm):
    """Та же форма смены пароля, но с bootstrap-классами на инпутах."""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for f in self.fields.values():
            f.widget.attrs.setdefault("class", "form-control")
