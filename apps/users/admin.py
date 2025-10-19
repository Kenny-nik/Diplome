from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import Group
from django.utils.translation import gettext_lazy as _

from .models import Profile

User = get_user_model()


# ---------------------------
# Профиль
# ---------------------------
@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "avatar_preview")
    search_fields = ("user__username", "user__email")
    readonly_fields = ("avatar_preview",)

    def avatar_preview(self, obj):
        if getattr(obj, "avatar", None):
            try:
                url = obj.avatar.url
                return admin.utils.format_html(
                    '<img src="{}" style="height:80px;border-radius:8px;" />', url
                )
            except Exception:
                return "—"
        return "—"

    avatar_preview.short_description = "Аватар"


# ---------------------------
# Экшены для User
# ---------------------------
@admin.action(description="Заблокировать пользователей (is_active = False)")
def deactivate_users(modeladmin, request, queryset):
    queryset.update(is_active=False)


@admin.action(description="Разблокировать пользователей (is_active = True)")
def activate_users(modeladmin, request, queryset):
    queryset.update(is_active=True)


@admin.action(description="Добавить в группу «Библиотекарь»")
def add_to_librarians_group(modeladmin, request, queryset):
    group, _ = Group.objects.get_or_create(name="Библиотекарь")
    for user in queryset:
        user.groups.add(group)


# ---------------------------
# Пользователь
# ---------------------------
@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """
    Кастом админки пользователя без ссылок на несуществующие поля.
    ВАЖНО: нигде не упоминаем поле is_librarian (его нет в модели).
    """

    # вычисляемый флаг «Библиотекарь» — либо staff, либо в группе «Библиотекарь»
    def is_librarian_flag(self, obj):
        try:
            return bool(obj.is_staff or obj.groups.filter(name="Библиотекарь").exists())
        except Exception:
            return False

    is_librarian_flag.boolean = True
    is_librarian_flag.short_description = "Библиотекарь"

    list_display = (
        "username",
        "email",
        "is_active",
        "is_staff",
        "is_superuser",
        "is_librarian_flag",
        "last_login",
        "date_joined",
    )
    list_filter = ("is_active", "is_staff", "is_superuser", "groups")
    search_fields = ("username", "email", "first_name", "last_name")
    ordering = ("-date_joined",)
    actions = (deactivate_users, activate_users, add_to_librarians_group)

    # Наборы полей формы изменения пользователя
    fieldsets = (
        (None, {"fields": ("username", "password")}),
        (_("Персональная информация"), {"fields": ("first_name", "last_name", "email")}),
        (
            _("Права"),
            {
                "fields": (
                    "is_active",
                    "is_staff",
                    "is_superuser",
                    "groups",
                    "user_permissions",
                )
            },
        ),
        (_("Важно"), {"fields": ("last_login", "date_joined")}),
    )

    # Наборы полей формы создания пользователя
    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": ("username", "email", "password1", "password2", "is_staff"),
            },
        ),
    )
