from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm, PasswordChangeForm

from .models import Profile

User = get_user_model()


# ---------- Регистрация ----------
class CustomUserCreationForm(UserCreationForm):
    """
    Регистрация по email + пароль.
    Если в модели есть username, заполняем его email'ом.
    """
    email = forms.EmailField(
        label="Email",
        required=True,
        widget=forms.EmailInput(attrs={
            "class": "form-control",
            "placeholder": "Введите ваш email",
        })
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["password1"].widget.attrs.update({
            "class": "form-control",
            "placeholder": "Введите пароль",
        })
        self.fields["password2"].widget.attrs.update({
            "class": "form-control",
            "placeholder": "Повторите пароль",
        })

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ("email",)

    def clean_email(self):
        email = (self.cleaned_data.get("email") or "").lower()
        if User.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError("Пользователь с таким email уже зарегистрирован.")
        return email

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data["email"].lower()
        # для стандартной модели добавим username = email
        if hasattr(user, "username") and not getattr(user, "username", ""):
            user.username = user.email
        if commit:
            user.save()
        return user


# ---------- Профиль пользователя ----------
class ProfileForm(forms.ModelForm):
    """
    Редактирование личных данных (instance=request.user).
    """
    class Meta:
        model = User
        fields = ("first_name", "last_name", "email")
        widgets = {
            "first_name": forms.TextInput(attrs={"class": "form-control", "placeholder": "Имя"}),
            "last_name": forms.TextInput(attrs={"class": "form-control", "placeholder": "Фамилия"}),
            "email": forms.EmailInput(attrs={"class": "form-control", "placeholder": "Email"}),
        }


# ---------- Аватар ----------
class AvatarForm(forms.ModelForm):
    """
    Загрузка/смена аватара (instance=profile).
    """
    class Meta:
        model = Profile
        fields = ("avatar",)
        widgets = {
            "avatar": forms.ClearableFileInput(attrs={"class": "form-control"}),
        }
        help_texts = {"avatar": "Поддерживаются JPG/PNG."}


# ---------- Смена пароля с Bootstrap-оформлением ----------
class StyledPasswordChangeForm(PasswordChangeForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["old_password"].widget.attrs.update({
            "class": "form-control",
            "placeholder": "Текущий пароль",
        })
        self.fields["new_password1"].widget.attrs.update({
            "class": "form-control",
            "placeholder": "Новый пароль",
        })
        self.fields["new_password2"].widget.attrs.update({
            "class": "form-control",
            "placeholder": "Подтверждение пароля",
        })
