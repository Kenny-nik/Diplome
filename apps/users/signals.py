from django.apps import apps
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from django.db.models.signals import m2m_changed, post_migrate
from django.dispatch import receiver

User = get_user_model()

LIBRARIAN_GROUP_NAME = "Библиотекарь"


@receiver(post_migrate)
def ensure_roles_and_permissions(sender, **kwargs):
    """
    Гарантируем, что после миграций есть группа «Библиотекарь»
    и у неё назначены базовые права на книги и займы.
    """
    group, _ = Group.objects.get_or_create(name=LIBRARIAN_GROUP_NAME)

    Book = apps.get_model("books", "Book")
    Loan = apps.get_model("loans", "Loan")

    ct_book = ContentType.objects.get_for_model(Book)
    ct_loan = ContentType.objects.get_for_model(Loan)

    need_codenames = {
        # Книги
        "view_book", "add_book", "change_book", "delete_book",
        # Займы
        "view_loan", "add_loan", "change_loan",
    }

    perms = Permission.objects.filter(
        content_type__in=[ct_book, ct_loan],
        codename__in=need_codenames,
    )
    group.permissions.add(*perms)


@receiver(m2m_changed, sender=User.groups.through)
def sync_staff_with_librarian_group(sender, instance: User, action, **kwargs):
    """
    После добавления/удаления групп у пользователя автоматически
    включаем/выключаем is_staff в зависимости от того,
    является ли он библиотекарем (или суперпользователем).
    """
    if action not in {"post_add", "post_remove", "post_clear"}:
        return

    in_librarians = instance.groups.filter(name=LIBRARIAN_GROUP_NAME).exists()
    new_is_staff = bool(instance.is_superuser or in_librarians)

    if instance.is_staff != new_is_staff:
        instance.is_staff = new_is_staff
        instance.save(update_fields=["is_staff"])
