from django.db import migrations


def create_roles(apps, schema_editor):
    Group = apps.get_model("auth", "Group")
    Permission = apps.get_model("auth", "Permission")
    ContentType = apps.get_model("contenttypes", "ContentType")

    admin_group, _ = Group.objects.get_or_create(name="Администратор сайта")
    librarian_group, _ = Group.objects.get_or_create(name="Библиотекарь")

    ct_books = ContentType.objects.filter(app_label__in=["books"]).values_list("id", flat=True)
    ct_loans = ContentType.objects.filter(app_label__in=["loans"]).values_list("id", flat=True)
    perms = Permission.objects.filter(content_type_id__in=list(ct_books) + list(ct_loans))

    admin_group.permissions.add(*perms)

    librarian_group.permissions.add(*perms)
    ct_users = ContentType.objects.filter(app_label="users").values_list("id", flat=True)
    users_change = Permission.objects.filter(content_type_id__in=ct_users, codename__startswith="change")
    librarian_group.permissions.add(*users_change)


def remove_roles(apps, schema_editor):
    Group = apps.get_model("auth", "Group")
    Group.objects.filter(name__in=["Администратор сайта", "Библиотекарь"]).delete()


class Migration(migrations.Migration):
    dependencies = [
        ("users", "0001_initial"),
        ("books", "0002_initial"),
        ("loans", "0001_initial"),
        ("auth", "0012_alter_user_first_name_max_length"),
    ]

    operations = [
        migrations.RunPython(create_roles, remove_roles),
    ]