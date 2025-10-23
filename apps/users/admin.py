from datetime import timedelta

from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import Group
from django.core.exceptions import FieldDoesNotExist
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from .models import Profile

User = get_user_model()


# ===== ВСПОМОГАТЕЛЬНОЕ =====
def profile_has_field(field_name: str) -> bool:
    """Проверяем, есть ли поле в модели Profile (чтобы админка не падала)."""
    try:
        Profile._meta.get_field(field_name)
        return True
    except FieldDoesNotExist:
        return False


# =========================
#  Профили
# =========================
@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    """Админка профиля: превью аватара + статус подписки (безопасно)."""
    list_display = ("user", "avatar_preview", "subscription_until_display")
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

    def _has_active(self, obj):
        """Активна ли подписка: дата >= сегодня или булев флаг."""
        until = getattr(obj, "subscription_until", None)
        if until:
            try:
                return until >= timezone.localdate()
            except Exception:
                pass
        has_flag = getattr(obj, "has_active_subscription", None)
        if isinstance(has_flag, bool):
            return has_flag
        return False

    def subscription_until_display(self, obj):
        """Безопасный вывод: дата если активна, иначе «—»."""
        until = getattr(obj, "subscription_until", None)
        if self._has_active(obj):
            return until or "Активна"
        return "—"

    subscription_until_display.short_description = "Подписка до"


# =========================
#  Inline профиль в карточке пользователя
# =========================
class ProfileInline(admin.StackedInline):
    """
    Редактируем профиль прямо в карточке пользователя.
    Поле subscription_until добавляем только если оно есть в модели.
    """
    model = Profile
    can_delete = False
    extra = 0
    readonly_fields = ("avatar_preview",)

    def get_fields(self, request, obj=None):
        base = ["avatar_preview", "avatar"]
        if profile_has_field("subscription_until"):
            base.append("subscription_until")
        elif profile_has_field("has_active_subscription"):
            base.append("has_active_subscription")
        return base

    # нужен для readonly_fields
    def avatar_preview(self, obj):
        if obj and getattr(obj, "avatar", None):
            try:
                url = obj.avatar.url
                return admin.utils.format_html(
                    '<img src="{}" style="height:80px;border-radius:8px;" />', url
                )
            except Exception:
                return "—"
        return "—"

    avatar_preview.short_description = "Аватар"

    def get_or_create_profile(self, obj):
        if obj and not getattr(obj, "profile", None):
            Profile.objects.get_or_create(user=obj)

    def get_formset(self, request, obj=None, **kwargs):
        if obj:
            self.get_or_create_profile(obj)
        return super().get_formset(request, obj, **kwargs)


# =========================
#  Фильтр «Премиум»
# =========================
class PremiumActiveFilter(admin.SimpleListFilter):
    title = "Премиум"
    parameter_name = "premium"

    def lookups(self, request, model_admin):
        return (("yes", "Активна"), ("no", "Нет"))

    def queryset(self, request, queryset):
        val = self.value()
        if not val:
            return queryset

        if profile_has_field("subscription_until"):
            today = timezone.localdate()
            if val == "yes":
                return queryset.filter(profile__subscription_until__gte=today)
            if val == "no":
                return queryset.exclude(profile__subscription_until__gte=today)
            return queryset

        if profile_has_field("has_active_subscription"):
            if val == "yes":
                return queryset.filter(profile__has_active_subscription=True)
            if val == "no":
                return queryset.filter(profile__has_active_subscription=False)
        return queryset


# =========================
#  Экшены для пользователей
# =========================
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


def _grant_until(profile: Profile, until):
    """Выдать подписку профилю с учётом наличия полей в модели."""
    if profile_has_field("subscription_until"):
        profile.subscription_until = until
        profile.save(update_fields=["subscription_until"])
        return "date"
    if profile_has_field("has_active_subscription"):
        profile.has_active_subscription = True
        profile.save(update_fields=["has_active_subscription"])
        return "flag"
    # если ни одного поля нет — просто создаём профиль и ничего не сохраняем
    if not getattr(profile, "pk", None):
        profile.save()
    return "none"


@admin.action(description="Премиум: выдать на 30 дней")
def grant_premium_30(modeladmin, request, queryset):
    today = timezone.localdate()
    until = today + timedelta(days=30)
    updated = 0
    for user in queryset:
        profile, _ = Profile.objects.get_or_create(user=user)
        _grant_until(profile, until)
        updated += 1
    modeladmin.message_user(request, f"Выдана подписка на 30 дней: {updated} пользователям.")


@admin.action(description="Премиум: выдать на 90 дней")
def grant_premium_90(modeladmin, request, queryset):
    today = timezone.localdate()
    until = today + timedelta(days=90)
    updated = 0
    for user in queryset:
        profile, _ = Profile.objects.get_or_create(user=user)
        _grant_until(profile, until)
        updated += 1
    modeladmin.message_user(request, f"Выдана подписка на 90 дней: {updated} пользователям.")


@admin.action(description="Премиум: продлить на 30 дней")
def extend_premium_30(modeladmin, request, queryset):
    today = timezone.localdate()
    updated = 0
    for user in queryset:
        profile, _ = Profile.objects.get_or_create(user=user)
        if profile_has_field("subscription_until"):
            base = profile.subscription_until or today
            profile.subscription_until = base + timedelta(days=30)
            profile.save(update_fields=["subscription_until"])
        elif profile_has_field("has_active_subscription"):
            profile.has_active_subscription = True
            profile.save(update_fields=["has_active_subscription"])
        updated += 1
    modeladmin.message_user(request, f"Подписка продлена/включена: {updated} пользователям.")


@admin.action(description="Премиум: снять подписку")
def revoke_premium(modeladmin, request, queryset):
    updated = 0
    for user in queryset:
        profile, _ = Profile.objects.get_or_create(user=user)
        if profile_has_field("subscription_until"):
            profile.subscription_until = None
            profile.save(update_fields=["subscription_until"])
        elif profile_has_field("has_active_subscription"):
            profile.has_active_subscription = False
            profile.save(update_fields=["has_active_subscription"])
        updated += 1
    modeladmin.message_user(request, f"Подписка снята: {updated} пользователям.")


# =========================
#  Пользователи
# =========================
@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """Админка пользователя + инлайн профиль + действия с подпиской."""
    inlines = (ProfileInline,)

    def is_librarian_flag(self, obj):
        if hasattr(obj, "is_librarian"):
            try:
                return bool(getattr(obj, "is_librarian"))
            except Exception:
                return False
        return obj.groups.filter(name="Библиотекарь").exists()

    is_librarian_flag.boolean = True
    is_librarian_flag.short_description = "Библиотекарь"

    def premium_until(self, obj):
        prof = getattr(obj, "profile", None)
        if prof and profile_has_field("subscription_until") and getattr(prof, "subscription_until", None):
            return prof.subscription_until
        # если дата отсутствует, но есть булев флаг — просто отметим галочкой
        if prof and profile_has_field("has_active_subscription"):
            return "✓" if getattr(prof, "has_active_subscription", False) else "—"
        return "—"

    premium_until.short_description = "Премиум до"

    list_display = (
        "username", "email", "is_active", "is_staff", "is_superuser",
        "is_librarian_flag", "premium_until", "last_login", "date_joined",
    )
    list_filter = ("is_active", "is_staff", "is_superuser", PremiumActiveFilter)
    search_fields = ("username", "email", "first_name", "last_name")
    ordering = ("-date_joined",)

    actions = (
        deactivate_users,
        activate_users,
        add_to_librarians_group,
        grant_premium_30,
        grant_premium_90,
        extend_premium_30,
        revoke_premium,
    )

    fieldsets = (
        (None, {"fields": ("username", "password")}),
        (_("Персональная информация"), {"fields": ("first_name", "last_name", "email")}),
        (_("Права"), {"fields": ("is_active", "is_staff", "is_superuser", "groups", "user_permissions")}),
        (_("Важно"), {"fields": ("last_login", "date_joined")}),
    )
    add_fieldsets = (
        (None, {
            "classes": ("wide",),
            "fields": ("username", "email", "password1", "password2", "is_staff"),
        }),
    )
