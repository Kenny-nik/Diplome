from django.db import migrations


def create_roles(apps, schema_editor):
    Group = apps.get_model("auth", "Group")
    Permission = apps.get_model("auth", "Permission")
    ContentType = apps.get_model("contenttypes", "ContentType")

    admin_group, _ = Group.objects.get_or_create(name="Администратор сайта")
    librarian_group, _ = Group.objects.get_or_create(name="Библиотекарь")

    ct_ids = list(ContentType.objects.filter(app_label__in=["books", "loans"]).values_list("id", flat=True))
    perms = list(Permission.objects.filter(content_type_id__in=ct_ids))

    admin_group.permissions.add(*perms)
    librarian_group.permissions.add(*perms)

    ct_user_ids = list(ContentType.objects.filter(app_label="users").values_list("id", flat=True))
    user_change_perms = list(Permission.objects.filter(content_type_id__in=ct_user_ids, codename__startswith="change"))
    librarian_group.permissions.add(*user_change_perms)


def remove_roles(apps, schema_editor):
    Group = apps.get_model("auth", "Group")
    Group.objects.filter(name__in=["Администратор сайта", "Библиотекарь"]).delete()


class Migration(migrations.Migration):
    dependencies = [
        ("users", "0002_profile_avatar_alter_profile_user"),
        ("books", "0006_remove_book_preview_text_alter_book_cover_url_and_more"),
        ("loans", "0001_initial"),
        ("auth", "0012_alter_user_first_name_max_length"),
    ]

    operations = [
        migrations.RunPython(create_roles, remove_roles),
    ]